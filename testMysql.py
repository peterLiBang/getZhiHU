#!/usr/bin/env python
#coding=utf8
import pymysql
import sys
# 打开数据库连接
db = pymysql.connect("localhost","root","123456","libq" )
# 使用cursor()方法获取操作游
cursor = db.cursor()
# SQL 插入语句
'''
sql = "INSERT INTO followers(leader_url_token, \
       url_token, IS_followed, avatar_url_temp, user_type,gender,follower_count,url,name,answer_count,is_advertiser,avatar_url,Is_following,is_org,headline,badge, \
       user_id,articles_count) \
       VALUES ('%s', '%s', '%s', '%s', '%s' ,'%d','%d','%s','%s','%d','%d','%s','%d','%d', '%s','%s','%s','%d' )" % \
       ('kaifulee', 'Mohan', 'sdsd', 'M','sd',0,1223,'seer','wewe', 2000,1,'sweqwe',1,1,'ewdf','dfre','ert',1334)
''' 	

sql = '''INSERT INTO USERINFO(url_token,is_followed, schoolName,majorName,following_count,vote_from_count,user_type, \
           show_sina_weibo,pins_count,is_following,marked_answers_text,is_force_renamed,user_id,favorite_count, \
           voteup_count,commercial_question_count,is_blocking,following_columns_count, \
           headline,participated_live_count,following_favlists_count,is_advertiser, \
           is_bind_sina,favorited_count,is_org,follower_count, avatar_url_template,following_topic_count, \
           description,avatar_url,hosted_live_count,is_active,thank_to_count,mutual_followees_count, \
           marked_answers_count,cover_url,thank_from_count,vote_to_count,is_blocked,answer_count,allow_message, \
           articles_count,name,question_count,locations,badge,url,message_thread_token,logs_count, \
           following_question_count,thanked_count,gender,sina_weibo_url,sina_weibo_name,business_name) \
         VALUES ('%s', '%d', '%s', '%s', '%d' ,'%d','%s', \
           '%d','%d','%d','%s','%d','%s','%d', \
           '%d','%d','%d','%d', \
           '%s','%d','%d','%d', \
           '%d','%d','%d','%d','%s','%d', \
           '%s','%s','%d','%d','%d','%d', \
           '%d','%s','%d','%d','%d','%d','%s', \
           '%d','%s','%d','%s','%s','%s','%s','%d', \
           '%d','%d','%d','%s','%s','%s');''' \
	%("aqiyi",0, "beijing", "IT",23,3, \
                "people",1,12,0,"22", \
                0, "3442", 324,32,32, \
                1,32,"my life",31,\
                123,1 ,1,123,\
                0,123,"23123",4,"hello",\
                "wwe",312,0,12 ,22,\
                34,"sdasd",24,34,1,\
                34,"23123",34,"wang",4,"lsodfj",\
                "null","sedqw","sde",23,45,\
                455,1,"http://baidu.com","sdas","csad")		
			
#sql = '''INSERT INTO USERINFO(url_token,is_followed, schoolName,majorName,following_count,vote_from_count,user_type,\
#		show_sina_weibo,pins_count,is_following,marked_answers_text,is_force_renamed,user_id,favorite_count)\
#         VALUES ('%s', '%d', '%s', '%s', '%d' ,'%d','%s',\
#		 '%d','%d','%d','%s','%d','%s','%d')''' \
#		%("libangqin1",2, "beijing", "IT",23,3,"people", \
#		  1,12,0,"22",1,"22",42)

print("sql = \n\n" + sql + "\n\n")          
	   
try:
   # 执行sql语句
   result = cursor.execute(sql)
   print "result = " + str(result)
   # 提交到数据库执行
   db.commit()
except:
   # 发生错误时回滚
   db.rollback()
# 关闭数据库连接
   db.close()
