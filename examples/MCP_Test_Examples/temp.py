import redis
import time
pool=redis.ConnectionPool(host='localhost',port=6379,decode_responses=False)
r=redis.Redis(connection_pool=pool)
r.set('testKey',1234,ex=3)
print(r.get('testKey'))
time.sleep(5)
print(r.get('testKey'))