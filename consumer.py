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
#gloable init
userInfoList = []
threadLock = threading.RLock()
endFlag = False
db = ''
db_cursor = ''
my_redis_con = None
#db init
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
        print("please check your db config")
        sys.exit()
#redis init
try:
      my_redis_host = dbConfig.get("redis", "host")
      my_redis_port = dbConfig.get("redis", "port")
      my_redis_con = redis.Redis(host = my_redis_host, port = my_redis_port, db=0)
except:
      print("please check your redis config!")
      sys.exit()
#

#logging model init
logging.basicConfig(level=logging.DEBUG,
          format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
          datefmt='%m-%d %H:%M',
          filename='zhihu.log',
          filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
getZhihuLog = logging.getLogger('getZhihuLog')
getZhihuLog.info('In consumer get ZhihuLog init success!')
getZhihuLog.debug('debug start...')



class UserInfoItem():
	is_followed  = None
	schoolName   = None
	majorName   = None	
	following_count = None
	vote_from_count  = None
	user_type   = None
	show_sina_weibo  = None
	pins_count   = None
	is_following  = None
	marked_answers_text  = None
#	account_status   = None #不获取此字段
	is_force_renamed  = None 
	user_id   = None
	favorite_count  = None 
	voteup_count  = None 
	commercial_question_count   = None 
	is_blocking   = None
	following_columns_count  = None
	headline   = None
	url_token   = None
	participated_live_count   = None
	following_favlists_count  = None
	is_advertiser   = None
	is_bind_sina   = None
	favorited_count  = None 
	is_org   = None
	follower_count  = None
	#employments  = None  #不获取
	user_type  = None
	avatar_url_template   = None
	following_topic_count  = None
	description   = None
	avatar_url  = None 
	hosted_live_count   = None
	is_active   = None
	thank_to_count   = None
	mutual_followees_count  = None 
	marked_answers_count  = None 
	cover_url   = None
	thank_from_count   = None
	vote_to_count   = None
	is_blocked   = None
	answer_count  = None
	allow_message   = None
	articles_count  = None
	name   = None
	question_count  = None
	locations   = None
	badge   = None
	url  = None
	message_thread_token   = None
	logs_count   = None
	following_question_count  = None 
	thanked_count  = None
	gender   = None
	sina_weibo_url   = None
	sina_weibo_name   = None
	business_name  = None
	def __init__(self):
		print("init userInfoItem....")

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
    retry = 3  #retry time
    redis_con = ''
    counter = 0  #counter user
    xsrf = ''
    max_queue_len = 1000  

    def __init__(self, threadID=1):
        getZhihuLog.info("prepar init :" + str(threadID) + "thread")
        threading.Thread.__init__(self)
        self.threadID = threadID
        try:
            getZhihuLog.info("thread init:" + str(threadID) + "success!")
        except Exception as err:
            print(err)
            getZhihuLog.error("thread init" + str(threadID) + "failed")

        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")

        requests.adapters.DEFAULT_RETRIES = 5
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookie')
        self.session.keep_alive = True
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            getZhihuLog.warn('get Cookie failed')
        finally:
            pass
        #
        lo = Login(self.session)
        lo.do_login()

    # get index_page html
    def get_index_page(self):
        index_url = 'https://www.zhihu.com/'
        try:
            index_html = self.session.get(index_url, headers=self.headers, timeout=66, verify=False)
        except Exception as err:
            getZhihuLog.warn("get index page failed......")
            print(err)
            traceback.print_exc()
            return None
        finally:
            pass
	#print index_html.text
        return index_html.text

    def get_xsrf(self):
        if self.xsrf:
            return self.xsrf
        # get xsrf
        index_page = self.get_index_page()
        if not index_page:
            getZhihuLog.warn(" get xsrf failed")
            sys.exit();
        BS = BeautifulSoup(index_page, 'lxml')
        xsrf_input = BS.find("input", attrs={'name': '_xsrf'})
        self.xsrf = xsrf_input.get("value")
        self.headers['X-Xsrftoken'] = self.xsrf
        self.session.cookies.save()
        getZhihuLog.info(u"xrsf is :" + self.xsrf)    

		
    def get_user_info(self,user_name):
	user_url = 'https://www.zhihu.com/api/v4/members/'+user_name+'?include=locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count%2Cfollowing_columns_count%2Canswer_count%2Carticles_count%2Cpins_count%2Cquestion_count%2Ccommercial_question_count%2Cfavorite_count%2Cfavorited_count%2Clogs_count%2Cmarked_answers_count%2Cmarked_answers_text%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_force_renamed%2Cis_bind_sina%2Csina_weibo_url%2Csina_weibo_name%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        try:
            index_html = self.session.get(user_url, headers=self.headers, timeout=66, verify=False)
        except Exception as err:
            #
            getZhihuLog.warn("get user INFO:" + str(user_url) + "failed")
            print(err)
            traceback.print_exc()
            return None
        finally:
            pass
	return index_html.text
	
    def userInfoPraser(self,htmlContent):
	item = UserInfoItem()
	userJson = json.loads(htmlContent)

	item.is_followed = 1 if userJson['is_followed'] else 0
	details = userJson['educations']
	if details is not None:
		print ("details len = " + str(len(details)))
		schoolNameList = []
		majorList = []
		for detail in details:
			try:
				school_name = detail['school']['name']
				print "school_name = " + school_name
			except:
				school_name = " "
				pass
			
			schoolNameList.append(school_name)
			try:
				major_name = detail['major']['name']
				print "major_name = " + major_name
			except:
				major_name = " "		
				print "major_name = " + major_name
				pass
			majorList.append(major_name)	
#handle school_name 
	tmpschool_name = ""
	if schoolNameList is not None:
	    	for tmp in schoolNameList:
			if tmp is not " ":
				tmpschool_name = tmpschool_name + tmp + ","
			else:
				tmpschool_name = tmpschool_name + "null,"
	item.schoolName = tmpschool_name
#handle major name
	tmpmajor_name = ""
	if majorList is not None:
                for tmp in majorList:
                        if tmp is not " ":
                                tmpmajor_name = tmpmajor_name + tmp + ","
                        else:
                                tmpmajor_name = tmpmajor_name + "null,"
        item.majorName = tmpmajor_name
	item.following_count = userJson['following_count']
	item.vote_from_count = userJson['vote_from_count']
#handle sina weibo
	tmp_show = item.show_sina_weibo = userJson['show_sina_weibo']
	if item.show_sina_weibo is True:
		try:
			item.sina_weibo_url = userJson['sina_weibo_url']#is_bind_sina 
			item.sina_weibo_name = userJson['sina_weibo_name'] #is_bind_sina
		except:
			item.sina_weibo_name = " "
			pass
# remake show_sina_weibo
	item.show_sina_weibo = 1 if tmp_show else 0	
	try:
		item.business_name = userJson['business']['name']
	except:
		item.business_name = " "
		pass
	print "business_name = " + item.business_name
	item.pins_count = userJson['pins_count']
	item.is_following =  1 if userJson['is_following'] else 0 
	item.marked_answers_text = userJson['marked_answers_text']
	item.is_force_renamed =  1 if userJson['is_force_renamed'] else 0
	item.user_id = userJson['id']
	item.favorite_count = userJson['favorite_count']
	item.voteup_count = userJson['voteup_count']
	item.commercial_question_count =  userJson['commercial_question_count']
	item.is_blocking = 1 if userJson['is_blocking'] else 0
	item.following_columns_count = userJson['following_columns_count']
	item.headline = userJson['headline']
	item.url_token = userJson['url_token']
	item.participated_live_count = userJson['participated_live_count']
	item.following_favlists_count = userJson['following_favlists_count']
	item.is_advertiser = 1 if userJson['is_advertiser'] else 0
	item.is_bind_sina  = 1 if userJson['is_bind_sina'] else 0
	item.favorited_count = userJson['favorited_count']
	item.is_org = 1 if userJson['is_org'] else 0
	item.follower_count = userJson['follower_count']
	item.avatar_url_template = userJson['avatar_url_template']
	item.following_topic_count = userJson['following_topic_count']
	item.description = userJson['description']
	item.avatar_url = userJson['avatar_url']
	item.hosted_live_count = userJson['hosted_live_count']
	item.is_active = 1 if userJson['is_active'] else 0
	item.thank_to_count = userJson['thank_to_count']
	item.mutual_followees_count = userJson['mutual_followees_count']
	item.marked_answers_count = userJson['marked_answers_count']
	item.cover_url = userJson['cover_url']
	item.thank_from_count = userJson['thank_from_count']
	item.vote_to_count = userJson['vote_to_count']
	item.is_blocked = 1 if userJson['is_blocked'] else 0
	item.answer_count = userJson['answer_count']
	item.allow_message = userJson['allow_message']
	item.articles_count = userJson['articles_count']
	item.name = userJson['name']
	item.question_count = userJson['question_count']
#handle locations
	locs = userJson['locations']
	if locs is not None:
                print ("locations len = " + str(len(locs)))
                locationList = []
                for detail in locs:
                        try:
                                locationName = detail['name']
                                print "locationName = " + locationName
                        except:
                                locationName = " "
                                pass
                        locationList.append(locationName)
	tmplocationName = ""
	if locationList is not None:
                for tmp in locationList:
                        if tmp is not " ":
                                tmplocationName = tmplocationName + tmp + ","
                        else:
                                tmplocationName = tmplocationName + "null,"
        item.locations = tmplocationName

	try:
		item.badge = userJson['badge']['topics']['name']
	except:
		item.badge = " "
		pass
	item.url = userJson['url']
	item.message_thread_token = userJson['message_thread_token']
	item.logs_count = userJson['logs_count']
	item.following_question_count = userJson['following_question_count']
	item.thanked_count = userJson['thanked_count']
	item.gender = userJson['gender']

	return item

    def consumerThread(self):
	if not endFlag:
		self.get_xsrf()
		self.session.cookies.save()
		while True:
			if my_redis_con.llen("user_queue") > 0:
				threadLock.acquire()
				name_url_token = str(my_redis_con.rpop("user_queue").decode('utf-8'))
				threadLock.acquire()
				getZhihuLog.info("prepar to get url_token detail info: " + name_url_token)
				userContent = self.get_user_info(name_url_token).encode('utf-8')
               			userItem = self.userInfoPraser(userContent)
				self.addItem2List(userItem)
				#随机休眠
				sleepTime = 1 + random.randint(1,4)
				print("now sleep :" + str(sleepTime)+"seconds .......")
				getZhihuLog.info("now sleep :" + str(sleepTime) + "seconds......")
				time.sleep(sleepTime)
			else:
				print("there not any more url in user_queue please wait...\n")
				getZhihuLog.warn("there not any url_token in user_queue please wait....")
				time.sleep(2) #
			self.session.cookies.save()

    def addItem2List(self,item):
		print(u"add user:"+ item.name + "to userInfoList !")
		userInfoList.append(item)
    def run(self):
        print("thread to get userDetailInfo is running.........")
        self.consumerThread()	



def addItem2Mysql(item):
	if item is None:
		print('item is null and quit!')
		sys.exit()			
	sql = "INSERT INTO USERINFO(url_token ,is_followed, schoolName,majorName,following_count,vote_from_count,user_type, \
           show_sina_weibo,pins_count,is_following,marked_answers_text,is_force_renamed,user_id,favorite_count, \
	   voteup_count,commercial_question_count,is_blocking,following_columns_count, \
	   headline,participated_live_count,following_favlists_count,is_advertiser, \
	   is_bind_sina,favorited_count,is_org,follower_count, avatar_url_template,following_topic_count, \
	   description,avatar_url,hosted_live_count,is_active,thank_to_count,mutual_followees_count, \
	   marked_answers_count,cover_url,thank_from_count,vote_to_count,is_blocked,answer_count,allow_message, \
	   articles_count,name,question_count,locations,badge,url,message_thread_token,logs_count, \
	   following_question_count,thanked_count,gender,sina_weibo_url,sina_weibo_name,business_name ) \
      	 VALUES ('%s', '%d', '%s', '%s', '%d' ,'%d','%s', \
	   '%d','%d','%d','%s','%d','%s','%d', \
	   '%d','%d','%d','%d', \
	   '%s','%d','%d','%d', \
	   '%d','%d','%d','%d','%s','%d', \
	   '%s','%s','%d','%d','%d','%d', \
	   '%d','%s','%d','%d','%d','%d','%s', \
	   '%d','%s','%d','%s','%s','%s','%s','%d',\
	   '%d','%d','%d','%s','%s','%s')" % \
       	(item.url_token, item.is_followed, item.schoolName, item.majorName,item.following_count,item.vote_from_count, \
		item.user_type,item.show_sina_weibo,item.pins_count,item.is_following,item.marked_answers_text, \
		item.is_force_renamed, item.user_id, item.favorite_count,item.voteup_count,item.commercial_question_count, \
	    	item.is_blocking,item.following_columns_count,item.headline,item.participated_live_count, \
		item.following_favlists_count,item.is_advertiser ,item.is_bind_sina,item.favorited_count,\
		item.is_org,item.follower_count,item.avatar_url_template,item.following_topic_count,item.description, \
		item.avatar_url,item.hosted_live_count,item.is_active,item.thank_to_count ,item.mutual_followees_count, \
		item.marked_answers_count,item.cover_url,item.thank_from_count,item.vote_to_count,item.is_blocked , \
		item.answer_count,item.allow_message,item.articles_count,item.name,item.question_count,item.locations, \
		item.badge,item.url,item.message_thread_token,item.logs_count,item.following_question_count,\
		item.thanked_count,item.gender,item.sina_weibo_url,item.sina_weibo_name,item.business_name)

	try:
	# 执行sql语句并提交到数据库
		result = db_cursor.execute(sql)
		print("exec result = " + str(result) + "\n" )
		db.commit()
	except:
		db.rollback()
		#db.close()


def watchThread():
	queueLen = 12
	if not endFlag:
                while True:
			print("In watchThread............................")
			getZhihuLog.info("In watchThread ....................")
			time.sleep(2)
                        userLen = len(userInfoList)
                        if userLen>=queueLen: 
                                print("prepare to write userInfo data to mysql")
				#threadLock.acquire()
			  	for i in range(0,queueLen/2):
					addItem2Mysql(userInfoList[i])	
					getZhihuLog.info("add user: " + userInfoList[i].url_token +"to mysql success!")
				for j in range(0,queueLen/2):
					del userInfoList[(queueLen/2-1)-i]
				userLen = len(userInfoList)
				print("len = " + str(userLen))
			        #threadLock.release()
                        else:
                                print(" is so less continue and len = " + str(userLen))				
if __name__ == '__main__':
    threads = []
    threadNums = 2
    n = threading.Thread(target = watchThread,args=())
    n.setDaemon(True)
    threads.append(n)
    for i in range(0,threadNums):
	m = GetUser(i)
   	threads.append(m)
    for i in range(0, len(threads)):
    	threads[i].start()
    for i in range(0,len(threads)):
	threads[i].join()

