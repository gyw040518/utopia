#coding=utf-8

from utopia import saltApi

params = {'client':'local', 'fun':'cmd.run', 'tgt':'*','arg1':'ifconfig | grep inet | grep 192.168 | awk \'{print( $2 )}\''}
sapi = saltApi.saltApi()
test = sapi.saltCmd(params)

print type(test)

print test

print test[0]["scm-splunkheader-192.168.218.212"]