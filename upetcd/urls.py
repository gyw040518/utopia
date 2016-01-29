# coding:utf-8
from django.conf.urls import patterns, include, url
from upetcd.views import *

urlpatterns = patterns('',
    url(r'^etcd/add/$', etcd_add, name='etcd_add'),
    url(r"^etcd/add_batch/$", etcd_add_batch, name='etcd_add_batch'),
    url(r'^etcd/list/$', etcd_list, name='etcd_list'),
    url(r'^etcd/del/$', etcd_del, name='etcd_del'),
    url(r"^etcd/detail/$", etcd_detail, name='etcd_detail'),
    url(r'^etcd/edit/$', etcd_edit, name='etcd_edit'),
    url(r'^etcd/edit_batch/$', etcd_edit_batch, name='etcd_edit_batch'),
    url(r'^etcd/update/$', etcd_update, name='etcd_update'),
    url(r'^etcd/update_batch/$', etcd_update_batch, name='etcd_update_batch'),
    url(r'^etcd/upload/$', etcd_upload, name='etcd_upload'),
    url(r'^group/del/$', group_del, name='etcd_group_del'),
    url(r'^group/add/$', group_add, name='etcd_group_add'),
    url(r'^group/list/$', group_list, name='etcd_group_list'),
    url(r'^group/edit/$', group_edit, name='etcd_group_edit'),
)
