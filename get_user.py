#!/bin/usr/env python
#encoding=utf-8
from login.login import Login as Login
import requests
import cookielib
import ConfigParser
from bs4 import BeautifulSoup
import sys
import redis
import json
import math
import re
import pymysql
import traceback
import threading
import lxml
import time
from lxml import html
import random 
import logging
reload(sys)
sys.setdefaultencoding('utf-8')

class UserItem():        
	leader_url_token = None
        url_token  = None#有用链接 需要配合urlshiyong 重要
	IS_followed = None #是否是关注者
        avatar_url_temp = None #背景头像链接 暂时没用
        gender = None # 性别
        name = None# name
        url = None #个人主页链接 需登录才能访问 暂时没用
        user_type = None #用户类型 
        answer_count = None #问答总数
        is_advertiser  = None# 
        avatar_url  = None# 头像
        Is_following = None # 
        is_org = None #
        headline = None #一句话介绍
        follower_count = None #追随者
        badge = None
        user_id  = None #用户id
        articles_count = None #文章数
        def __init__(self):
                print"init UserItem"
#全局变量及初始化

followerList = []
endFlag = False
threadLock = threading.RLock()
db = ''
db_cursor = ''
my_redis_con = None
user_name = None
# 初始化数据库连接
try:
	dbConfig = ConfigParser.ConfigParser()
        dbConfig.read("config.ini")
        db_host = dbConfig.get("db", "host")
        db_port = int(dbConfig.get("db", "port"))
        db_user = dbConfig.get("db", "user")
        db_pass = dbConfig.get("db", "password")
        db_db = dbConfig.get("db", "db")
        db_charset = dbConfig.get("db", "charset")
        db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_db,
                                     charset=db_charset)
        db_cursor = db.cursor()
except:
        print("请检查数据库配置")
        sys.exit()
#初始化redis连接
try:
      my_redis_host = dbConfig.get("redis", "host")
      my_redis_port = dbConfig.get("redis", "port")
      my_redis_con = redis.Redis(host = my_redis_host, port = my_redis_port, db=0)
except:
      print("请安装redis或检查redis连接配置")
      sys.exit()
#初始化日志模块

# 配置日志信息
logging.basicConfig(level=logging.DEBUG,
          format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
          datefmt='%m-%d %H:%M',
          filename='zhihu.log',
          filemode='a')
# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 设置日志打印格式
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
#实现同时在终端标准输出和记录到日志文件功能!
logging.getLogger('').addHandler(console)
getZhihuLog = logging.getLogger('getZhihuLog')
getZhihuLog.info('get ZhihuLog init success!')
getZhihuLog.debug('debug start...')


class GetUser(threading.Thread):
    session = ''
    config = ''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com/",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Pragma": "no-cache",
	"authorization":" Bearer Mi4wQUlCQUxIb3AyQW9BRUlJMlZzZGNDeVlBQUFCZ0FsVk5XWGpZV0FEYjhYeXB2aWNjVWs4aVBxWUx0LXM3TGI0ZTV3|1487993703|2928af200468e4a4fc0b481dd22a623b961dd224",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"	
        #'Connection': 'keep-alive'
    }
    retry = 3  # 重试次数
    redis_con = ''
    counter = 0  # 被抓取用户计数
    xsrf = ''
    max_queue_len = 1000  # redis带抓取用户队列最大长度
    threadID = None
    offset = 0
    totals = 0 
    #user_name = None
	
    def __init__(self, threadID=1, name='kaifulee'):
        # 多线程
        getZhihuLog.info("线程" + str(threadID) + "初始化")
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        try:
            getZhihuLog.info("线程" + str(threadID) + "初始化成功")
        except Exception as err:
            print(err)
            getZhihuLog.error("线程" + str(threadID) + "开启失败")

        # 获取配置
        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")

        # 初始化session
        requests.adapters.DEFAULT_RETRIES = 5
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookie')
        self.session.keep_alive = True
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            getZhihuLog.warn('Cookie 未能加载')
        finally:
            pass
        # 创建login对象
        lo = Login(self.session)
        lo.do_login()

        # 初始化redis连接
        try:
            redis_host = self.config.get("redis", "host")
            redis_port = self.config.get("redis", "port")
            self.redis_con = redis.Redis(host=redis_host, port=redis_port, db=0)
            # 刷新redis库
            # self.redis_con.flushdb()
        except:
            getZhihuLog.error("请安装redis或检查redis连接配置")
            sys.exit()
	    #self.max_queue_len = int(self.config.get("sys", "max_queue_len"))

    # 获取首页html
    def get_index_page(self):
        index_url = 'https://www.zhihu.com/'
        try:
            index_html = self.session.get(index_url, headers=self.headers, timeout=66, verify=False)
        except Exception as err:
            # 出现异常重试
            getZhihuLog.warn(u"获取页面失败，正在重试......")
            print(err)
            traceback.print_exc()
            return None
        finally:
            pass
	#print index_html.text
        return index_html.text

    # 获取xsrf保存到header
    def get_xsrf(self):
        if self.xsrf:
            return self.xsrf
        # 获取index页面来获取xsrf
        index_page = self.get_index_page()
        # 判断是否获取到index页面
        if not index_page:
            getZhihuLog.warn(u"获取xsrf失败，退出")
            sys.exit();
        BS = BeautifulSoup(index_page, 'lxml')
        xsrf_input = BS.find("input", attrs={'name': '_xsrf'})
        self.xsrf = xsrf_input.get("value")
        self.headers['X-Xsrftoken'] = self.xsrf
        self.session.cookies.save()
        getZhihuLog.info(u"获取到xsrf：" + self.xsrf)
    
    # 加入待抓取用户队列，先用redis判断是否已被抓取过
    def add_wait_user(self, name_url):
        # 判断是否已抓取
        is_exist = False
	threadLock.acquire()
        if not self.redis_con.hexists('already_get_user', name_url):
            self.counter += 1
            print(name_url + "add 2 user list")
            self.redis_con.hset('already_get_user', name_url, 1)
            self.redis_con.lpush('user_queue', name_url)
	    self.redis_con.lpush('prepare_user_queue', name_url)
            print("add user: " + name_url + "to list success!") 
            getZhihuLog.info(u"添加用户 " + name_url + u"到队列成功!")
	else:
	    is_exist = True
        threadLock.release()
	return is_exist

    # 获取页面出错移出redis
    def del_already_user(self, name_url):
        threadLock.acquire()
        if not self.redis_con.hexists('already_get_user', name_url):
            self.counter -= 1
            self.redis_con.hdel('already_get_user', name_url)
        threadLock.release()
	
    def saveLastUrl(self,last_url):
	print("save URL in thread"+str(self.threadID)+"\n")
	self.redis_con.hset('last_url_map', "thread"+str(self.threadID), last_url)
    
    def add_item2List(self,item):
	threadLock.acquire()
        if item is not None:
            followerList.append(item)
        threadLock.release()

    def jsonParser(self,htmlContent,leader_name):
	hjson = json.loads(htmlContent)
	if( self.totals == 0 ):
		self.totals = hjson['paging']['totals']
		print "totals =  " +str(self.totals)
		getZhihuLog.info("totals = "+str(self.totals))
	is_end = False 
	if self.offset > self.totals:
		is_end = True
	#is_end = hjson['paging']['is_end']
	if is_end is False:
	#	next_url = self.get_followees_url(leader_name,self.offset)
		self.offset = self.offset + 20 
		next_url = hjson['paging']['next']
	else:
		print('End to scrapy that gay!')
		next_url = ''
	personDatas = hjson['data']
	if personDatas is not None:
		for person in personDatas:
			self.getUserDetail(json.dumps(person),leader_name) 
	else:
		print "there nothing to get!"
	print ("next_url = "+next_url)
	getZhihuLog.info("next_url = "+ next_url)
	return next_url
		 
    def getUserDetail(self,person,leader_name):
	item = UserItem()
	detailJson = json.loads(person)
	item.leader_url_token = leader_name
	item.Is_followed = str( 1 if detailJson['is_followed'] else 0 )
	item.avatar_url_temp = detailJson['avatar_url_template']
	item.gender = str(detailJson['gender'])
	
	item.name = detailJson['name']
	item.url = detailJson['url']
	item.user_type = detailJson['type']
	item.answer_count = str(detailJson['answer_count'])
	item.url_token = detailJson['url_token']
	item.is_advertiser = str( 1 if detailJson['is_advertiser'] else 0 )
	item.avatar_url = detailJson['avatar_url']
	item.Is_following = str( 1 if detailJson['is_following'] else 0 )
	item.is_org = str( 1 if detailJson['is_org'] else 0 )
	item.headline = detailJson['headline']
	item.follower_count = str(detailJson['follower_count'])
	item.badge = detailJson['badge']
	item.user_id = detailJson['id']
	item.articles_count = str(detailJson['articles_count'])
	if(item.url_token is None):
		print("We need to quit now!")
		sys.exit()
	print("prepar add item : " + item.url_token + " to list!\n")	
	
	getZhihuLog.info("prepar add item : " + item.url_token + " to list!")
	already_get_flag = self.add_wait_user(item.url_token)
	if already_get_flag is False:
		self.add_item2List(item)
	else:
		print(" That user :" + item.url_token + "has exist !\n\n")
		getZhihuLog.warn(" That user :" + item.url_token + "has exist !")
    def get_followers_url(self,name,offset):
	followersUrl = "https://www.zhihu.com/api/v4/members/"+name+"/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset="+str(offset)+"&limit=20"
	return followersUrl

    def get_followees_url(self,name,offset):
	followeesUrl = "https://www.zhihu.com/api/v4/members/"+name +"/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset="+str(offset)+"&limit=20"
	return followeesUrl

    #获取追随者列表
    def get_followers(self,name_url,continueFlag):
	#入参 解析name_url在continueFlag为true时是url地址
	#user_name = None
	if continueFlag is False:
		next_url = self.get_followers_url(name_url,0)
		self.add_wait_user(name_url)
		self.del_prepare_user(name_url)
	else: 
		next_url = name_url 
		self.name = self.get_name_from_url(name_url)
		print("del that user: " + self.name)
		self.del_prepare_user(self.name)
		
	while next_url != '':
	   	followerJson = self.session.get(next_url, headers=self.headers, timeout=66, verify=False)
	    	next_url = self.jsonParser(followerJson.text.encode('utf-8'),self.name)
		self.saveLastUrl(next_url)
		print("sssssssssssssssssss....................\n")
		sleepTime = 3 + random.randint(1,10)
		getZhihuLog.info("sleep " + str(sleepTime) + " seconds..............")
		time.sleep(sleepTime)
	#结束表示该name_url对应的关注列表已经获取完毕 应该冲prepare_user_queue中pop出

    def get_name_from_url(self,name_url):
	user_name = None 
	firstIndex = name_url.find('members/')
        secondIndex = name_url.find('/followers')
	user_name =  name_url[firstIndex+8 : secondIndex]
	return user_name 

    def get_offset_from_url(self,name_url):
	offset = 0
	firstIndex = name_url.find('offset')
	strLen = len(name_url)
	offset = int(name_url[firstIndex+7:strLen])
	return offset    

    def del_prepare_user(self,user_name):
	threadLock.acquire()
	result = self.redis_con.lrem("prepare_user_queue",user_name,0)
	threadLock.release()
	getZhihuLog.info("that user:"+ user_name +" has been scrapy!")
		
    # 开始抓取用户，程序总入口
    def entrance(self,name_url):
	#startName = "kaifulee"
        #startName="huangmenglong"
	self.get_xsrf()
	self.session.cookies.save()
	continueFlag = False
	while True:
            if int(self.redis_con.llen("user_queue")) <= 20:
		print("new job and prepar to get user!")
		self.get_followers(name_url,continueFlag)
            else:
                # 出队列获取用户name_url redis取出的是byte，要decode成utf-8
		if continueFlag is False:
			try:
				name_url = str(self.redis_con.hget("last_url_map","thread"+str(self.threadID)).decode('utf-8'))
			except:
				name_url = None
			continueFlag = True
			if name_url is not None and name_url is not '':
				self.offset = self.get_offset_from_url(name_url)
				self.get_followers(name_url,continueFlag)
				print("continue to work....\n\n")
			else:
				pass
		else:
		#here mind that a user has been compele scrapy that we get next
	    		self.session.cookies.save()
			name = str(self.redis_con.rpop("prepare_user_queue").decode('utf-8'))
			name_url = self.get_followers_url(name,0)
			#totals set 0
			self.offset = 0
			self.totals = 0 
			self.get_followers(name_url,continueFlag)
	    self.session.cookies.save()

    def run(self):
        print("thread to get:" + self.name + " is running.........")
        self.entrance(self.name)

def addItem2Mysql(item):
	if item is None:
		print('item is null and quit!')
		
	sql = "INSERT INTO FOLLOWERS(leader_url_token, \
       url_token, IS_followed, avatar_url_temp, user_type,gender,follower_count,url,name,answer_count,is_advertiser,avatar_url,Is_following,is_org,headline,badge, \
       user_id,articles_count) \
       VALUES ('%s', '%s', '%d', '%s', '%s' ,'%d','%d','%s','%s','%d','%d','%s','%d','%d', '%s','%s','%s','%d' )" % \
       (item.leader_url_token+'_' + item.url_token, item.url_token, int(item.Is_followed), item.avatar_url_temp,item.user_type,int(item.gender), \
int(item.follower_count),item.url,item.name, int(item.answer_count),int(item.is_advertiser),item.avatar_url, \
	   int(item.Is_following),int(item.is_org),item.headline,item.badge,item.user_id,int(item.articles_count))
	try:
	# 执行sql语句并提交到数据库
		db_cursor.execute(sql)
		db.commit()
	except:
	# 发生错误时回滚并且关闭数据库连接
		db.rollback()
		#db.close()
#followerList监控函数
def watchThread():
	if not endFlag:
                while True:
			time.sleep(2)
                        followersLen = len(followerList)
                        if followersLen>=200: 
                                print("write data to mysql")
				threadLock.acquire()
			  	for i in range(0,100):
					print("add \t" + followerList[i].url_token +" ....\n")	
					getZhihuLog.info("add \t " + followerList[i].url_token +"to mysql success!")
					addItem2Mysql(followerList[i])
				for j in range(0,100):
					del followerList[99-i]
				followersLen = len(followerList)
				print("len = " + str(followersLen))
			        threadLock.release()
                        else:
                                print(" is so less continue and len = " + str(followersLen))
if __name__ == '__main__':
    userConsumer = GetUser(10,"user consumer thread!")
    threads = []
    threads_num = 4
    start_name_urls=['kaifulee','shen','yangbo','hecaitou']
    #start_name_urls=['li-zhi-yuan-22','ni-mei-liao-mei','time-my-50','hera-siu']
    n = threading.Thread(target = watchThread,args = ())
    threads.append(n)  
	
    for i in range(0, threads_num):
        m = GetUser(i, start_name_urls[i])
        threads.append(m)
 
    for i in range(0, threads_num + 1):
        threads[i].start()

		
    for i in range(0, threads_num + 1):
        threads[i].join()
