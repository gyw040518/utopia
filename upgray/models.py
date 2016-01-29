# coding: utf-8

from django.db import models
from upuser.models import User, UserGroup
from upasset.models import Asset

RULE_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"已报废")
    )

class Rule(models.Model):
    name = models.CharField(unique=True, max_length=128, verbose_name=u"规则名称")
    shortname = models.CharField(unique=True, max_length=128, verbose_name=u"规则简称")
    content = models.TextField(blank=True, null=True, default='', verbose_name=u"规则内容")
    status = models.IntegerField(choices=RULE_STATUS, blank=True, null=True, default=1, verbose_name=u"规则状态")
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    date_added = models.DateTimeField(auto_now=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")
    use_default_auth = models.BooleanField(default=True, verbose_name=u"使用默认管理账号")
    def __unicode__(self):
        return self.name

class RuleRecord(models.Model):
    rule = models.ForeignKey(Rule)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class RuleAlias(models.Model):
    user = models.ForeignKey(User)
    rule = models.ForeignKey(Rule)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias


class System(models.Model):
    name = models.CharField(unique=True, max_length=128, verbose_name=u"系统名称")
    rule_name = models.ForeignKey(Rule, blank=True, null=True, verbose_name=u'规则名称')
    old_version = models.TextField(blank=True, null=True, default='', verbose_name=u"A版本流量")
    new_version = models.TextField(blank=True, null=True, default='', verbose_name=u"B版本流量")
    status = models.IntegerField(choices=RULE_STATUS, blank=True, null=True, default=1, verbose_name=u"系统状态")
    date_added = models.DateTimeField(auto_now=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")
    use_default_auth = models.BooleanField(default=True, verbose_name=u"使用默认管理账号")

    def __unicode__(self):
        return self.name

class SystemRecord(models.Model):
    system = models.ForeignKey(System)
    alert_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class SystemAlias(models.Model):
    user = models.ForeignKey(User)
    system = models.ForeignKey(System)
    alias = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.alias