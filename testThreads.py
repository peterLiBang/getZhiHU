#!/bin/usr/env python
#coding=utf8
import threading
import sys
import time
def testThread(index,name):
	print("index = " + str(index) + " name = " + name +" sleep....")
	time.sleep(5)
def watchThread():
	for i in range(0,5):
		time.sleep(1)
		print("count time....")
if __name__ == '__main__':
	threads = []
	threads_num = 4
    	start_name_urls=['kaifulee','shen','yangbo','hecaitou']
   	for i in range(0, threads_num):
       		m = threading.Thread(target = testThread,args=(i, start_name_urls[i]))
        	threads.append(m)
	n = threading.Thread(target  = watchThread,args = ())
	threads.append(n)
    	for i in range(0, threads_num + 1):
        	threads[i].start()

    	for i in range(0, threads_num + 1):
        	threads[i].join()

