# coding:utf-8
from django.conf.urls import patterns, url
from upgray.views import *

urlpatterns = patterns('',
    url(r'^grule/add/$', rule_add, name='grule_add'),
    url(r'^grule/list/$', rule_list, name='grule_list'),
    url(r'^grule/del/$', rule_del, name='grule_del'),
    url(r"^grule/detail/$", rule_detail, name='grule_detail'),
    url(r'^grule/edit/$', rule_edit, name='grule_edit'),
    url(r'^grule/update/$', rule_update, name='grule_update'),
    url(r'^system/list/$', system_list, name='system_list'),
    url(r'^system/add/$', system_add, name='system_add'),
    url(r'^system/detail/$', system_detail, name='system_detail'),
    url(r'^system/edit/$', system_edit, name='system_edit'),
    url(r'^system/del/$', system_del, name='system_del'),
    url(r'^system/update/$', system_update, name='system_update'),
)
