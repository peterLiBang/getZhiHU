import redis
redis_con = redis.Redis(host='127.0.0.1', port=6379, db=0)
print("user_queue length:"+str(redis_con.llen('user_queue')))
print("already_get_user length:"+str(redis_con.hlen("already_get_user")))
print("last_url_map length:"+str(redis_con.hlen("last_url_map")))
print("prepare_user_queue length:"+str(redis_con.llen("prepare_user_queue")))
