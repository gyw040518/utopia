# coding: utf-8
from upgray.gray_api import redisconnect

obj = redisconnect()

def oldadd(a):
    obj.sadd('dopold',a)

def newadd(a):
    obj.sadd('dopnew',a)

def new2old(a):
    p = obj.pipeline()
    p.srem('dopnew',a)
    p.sadd('dopold',a)
    p.execute()

def old2new(a):
    p = obj.pipeline()
    p.srem('dopold',a)
    p.sadd('dopnew',a)
    p.execute()

print "走新版本的：",obj.smembers('dopnew')
print "走老版本的：",obj.smembers('dopold')

#test
#curl -d "ecCompanyId=tianmao" "http://192.168.218.97:8084/cnInterface/abc"
#curl -o /dev/null -s -w '%{time_connect}:%{time_starttransfer}:%{time_total}:%{time_namelookup}:%{speed_download}\n' -d "ecCompanyId=tianmao" "http://10.224.70.146:8081/cnInterface/abc"
#curl -o /dev/null -s -w '%{time_connect}:%{time_starttransfer}:%{time_total}:%{time_namelookup}:%{speed_download}\n' -d "ecCompanyId=tianmao" "http://10.224.70.146:8082/cnInterface/abc"