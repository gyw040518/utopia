#coding=utf-8

from upetcd.etcd_api import EtcdConnect, etcdconnect

Dir = "/v2/keys/registry/minions"
a = etcdconnect().read(Dir)
print a
print a._children

print type(a._children)

for m in a._children:
    print m['key']
