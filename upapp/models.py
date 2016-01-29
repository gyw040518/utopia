# coding: utf-8

import datetime
from django.db import models
from upuser.models import User, UserGroup
from upasset.models import Asset
from upenv.models import ENV_ENVS


APP_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"已报废")
    )

APP_TYPE = (
    (1, u"JBOSS-5"),
    (2, u"JBOSS-6"),
    (3, u"JBOSS-7"),
    (4, u"TOMCAT-6"),
    (5, u"TOMCAT-7"),
    (6, u"PYTHON-2"),
    (7, u"PYTHON-3"),
    (8, u"PHP-5"),
    (9, u"GO-1.5")
    )

PROC_TYPE = (
    (1,u"ajp协议"),
    (2,u"http协议"),
    (3,u"四层协议"),
    (4,u"七层协议"),
    (5,u"其他协议")
    )

class AppGroup(models.Model):
    GROUP_TYPE = (
        ('P', 'PRIVATE'),
        ('A', 'APP'),
    )
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name




class App(models.Model):
    """
    app modle
    """
    name = models.CharField(unique=True, max_length=128, verbose_name=u"应用名称")
    group = models.ManyToManyField(AppGroup, blank=True, verbose_name=u"应用组")
    status = models.IntegerField(choices=APP_STATUS, blank=True, null=True, default=1, verbose_name=u"应用状态")
    app_type = models.IntegerField(choices=APP_TYPE, blank=True, null=True, verbose_name=u"应用类型")
    use_default_auth = models.BooleanField(default=True, verbose_name=u"使用默认管理账号")
    date_added = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name


class AppRecord(models.Model):
    app = models.ForeignKey(App)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class AppAlias(models.Model):
    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias


class Map(models.Model):
    """
    map modle
    """
    name = models.ForeignKey(App, blank=True, verbose_name=u"应用名称")
    node_ip = models.ManyToManyField(Asset, blank=True, verbose_name=u"节点IP")
    node = models.CharField(max_length=128, verbose_name=u"节点名称")
    path = models.CharField(max_length=128, verbose_name=u"部署路径")
    contextroot = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"ContextRoot")
    group = models.ManyToManyField(AppGroup, blank=True, verbose_name=u"应用组")
    use_default_auth = models.BooleanField(default=True, verbose_name=u"使用默认管理账号")
    map_envs = models.IntegerField(choices=ENV_ENVS, blank=True, null=True, verbose_name=u"运行环境")
    date_added = models.DateTimeField(auto_now=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

class MapRecord(models.Model):
    map = models.ForeignKey(Map)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class MapAlias(models.Model):
    user = models.ForeignKey(User)
    map = models.ForeignKey(Map)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias

class Web(models.Model):
    """
    Web modle
    """
    name = models.ForeignKey(App, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u"应用名称")
    web_ip = models.ManyToManyField(Asset, blank=True, verbose_name=u"web主机")
    web_port = models.CharField(max_length=128, verbose_name=u"web端口")
    protocol_type = models.IntegerField(choices=PROC_TYPE, blank=True, null=True, verbose_name=u"协议类型")
    app_env = models.IntegerField(choices=ENV_ENVS, blank=True, null=True, verbose_name=u"运行环境")
    date_added = models.DateTimeField(auto_now=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

class WebRecord(models.Model):
    web = models.ForeignKey(Web)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class WebAlias(models.Model):
    user = models.ForeignKey(User)
    web = models.ForeignKey(Web)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias

class Dns(models.Model):
    """
    Dns modle
    """
    name = models.ForeignKey(App, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u"应用名称")
    url = models.CharField(max_length=128, verbose_name=u"域名地址")
    vip = models.CharField(max_length=128, verbose_name=u"虚拟IP")
    vport = models.CharField(max_length=128, verbose_name=u"虚拟端口")
    rip = models.ManyToManyField(Asset, blank=True, verbose_name=u"真实主机")
    rport = models.CharField(max_length=128, verbose_name=u"真实端口")
    protocol_type = models.IntegerField(choices=PROC_TYPE, blank=True, null=True, verbose_name=u"协议类型")
    app_env = models.IntegerField(choices=ENV_ENVS, blank=True, null=True, verbose_name=u"运行环境")
    date_added = models.DateTimeField(auto_now=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

class DnsRecord(models.Model):
    dns = models.ForeignKey(Dns)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class DnsAlias(models.Model):
    user = models.ForeignKey(User)
    dns = models.ForeignKey(Dns)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias
