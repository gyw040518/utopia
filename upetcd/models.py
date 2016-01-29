# coding: utf-8

from django.db import models
from upuser.models import User, UserGroup
from upenv.models import ENV_ENVS


ETCD_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"已报废")
    )

ETCD_TYPE = (
    (1, u"网站URL"),
    (2, u"接口URL"),
    (3, u"IP地址"),
    (4, u"密码参数"),
    (5, u"数值参数"),
    (6, u"其他参数")
    )


class EtcdGroup(models.Model):
    GROUP_TYPE = (
        ('P', 'PRIVATE'),
        ('A', 'ETCD'),
    )
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Etcd(models.Model):
    """
    etcd modle
    """
    name = models.CharField(unique=True, max_length=128, verbose_name=u"参数名")
    value = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"参数值")
    appname = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"应用名称")
    pre_value = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"原参数值")
    group = models.ManyToManyField(EtcdGroup, blank=True, verbose_name=u"参数组")
    status = models.IntegerField(choices=ETCD_STATUS, blank=True, null=True, default=1, verbose_name=u"参数状态")
    etcd_type = models.IntegerField(choices=ETCD_TYPE, blank=True, null=True, verbose_name=u"参数类型")
    etcd_env = models.IntegerField(choices=ENV_ENVS, blank=True, null=True, verbose_name=u"运行环境")
    use_default_auth = models.BooleanField(default=True, verbose_name=u"使用默认管理账号")
    date_added = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.value


class EtcdRecord(models.Model):
    etcd = models.ForeignKey(Etcd)
#    username = models.CharField(max_length=30, null=True)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class EtcdAlias(models.Model):
    user = models.ForeignKey(User)
    etcd = models.ForeignKey(Etcd)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias
