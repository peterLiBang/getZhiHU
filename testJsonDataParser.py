#!/bin/usr/env python
#coding=utf8
import re 
import json
class UserItem():
	IS_followed = None #是否是关注者
	avatar_url_temp = None #头像链接
	gender = None # 性别
	name = None# name
	url = None #个人主页链接 需登录才能访问
	user_type = None #用户类型
	answer_count = None #问答总数
	url_token  = None#有用链接 需要配合urlshiyong
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

def jsonParser(htmlContent):
	hjson = json.loads(htmlContent)
	is_end = hjson['paging']['is_end']
	if is_end is not False:
		next_url = hjson['paging']['next']
	personDatas = hjson['data']
	#print ("lens = " + str(len(personDatas)))
	if personDatas is not None:
		for person in personDatas:
			#print("person Type = " + str(type(person)) )
			getUserDetail(json.dumps(person)) 
	else:
		print "there nothing to get!"
	#print ("lens = " + str(len(personDatas)))

def userInfoPraser(htmlContent):
	userJson = json.loads(htmlContent)
	is_followed = userJson['is_followed']
	details = education_school = userJson['educations']
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
	tmpschool_name = ""
        for tmp in schoolNameList:
                if tmp is not " ":
                        tmpschool_name = tmpschool_name + tmp + ","
                else:
                        tmpschool_name = tmpschool_name + "null,"
        print "after handler : " + tmpschool_name	
	
	following_count = userJson['following_count']
	vote_from_count = userJson['vote_from_count']
	user_type = userJson['user_type']
	show_sina_weibo = userJson['show_sina_weibo']
        if show_sina_weibo is True:
		try:
			sina_weibo_url = userJson['sina_weibo_url']#is_bind_sina 
			sina_weibo_name = userJson['sina_weibo_name'] #is_bind_sina
		except:
			sina_weibo_name = ""
			pass
        pins_count = userJson['pins_count']
	is_following = userJson['is_following']
	marked_answers_text = userJson['marked_answers_text']
	try:
		business_name = userJson['business']['name']
	except:
		business_name = ""
		pass
	print "business_name = " + business_name
	name = userJson['name'] 

def getUserDetail(person):
	item = UserItem()
	detailJson = json.loads(person)
	item.Is_followed = detailJson['is_followed']
	item.avatar_url_temp = detailJson['avatar_url_template']
	item.gender = detailJson['gender']
	item.name = detailJson['name']
	item.url = detailJson['url']
	item.user_type = detailJson['type']
	item.answer_count = detailJson['answer_count']
	item.url_token = detailJson['url_token']
	item.is_advertiser = detailJson['is_advertiser']
	item.avatar_url = detailJson['avatar_url']
	item.Is_following = detailJson['is_following']
	item.is_org = detailJson['is_org']
	item.headline = detailJson['headline']
	item.follower_count = detailJson['follower_count']
	item.badge = detailJson['badge']
	item.user_id = detailJson['id']
	item.articles_count = detailJson['articles_count']
	print item.url_token
	name_url = "https://www.zhihu.com/people/" + item.url_token +"/answers" 
	print("prepar turn to url:" +  name_url)
	
if __name__=='__main__':
	
#	with open('jsonData.txt') as json_file:
#		jsonData = json.load(json_file)
#		htmlContent = json.dumps(jsonData)
	#print str(type(htmlContent))
#	jsonParser(htmlContent)

	with open('userInfo.json') as user_json_file:
		user_json = json.load(user_json_file)
		userInfoHtml = json.dumps(user_json)
	userInfoPraser(userInfoHtml)


