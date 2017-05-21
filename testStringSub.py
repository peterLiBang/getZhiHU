#!/bin/usr/env python
#coding=utf8



if __name__ == "__main__":
	name = "little"
	test = "https://www.zhihu.com/api/v4/members/"+name+"/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20";
	firstIndex = test.find('members/')
	secondIndex = test.find('/followers')
	print("firstIndex = "+str(firstIndex) +"and secondIndex = "+str(secondIndex))	

