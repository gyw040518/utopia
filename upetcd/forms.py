# coding:utf-8
from django import forms

from upetcd.models import Etcd, EtcdGroup


class EtcdForm(forms.ModelForm):

    class Meta:
        model = Etcd

        fields = [
            "value", "appname", "pre_value", "name", "group", "status", "use_default_auth", "etcd_type", "etcd_env", "is_active", "comment"
        ]


class EtcdGroupForm(forms.ModelForm):
    class Meta:
        model = EtcdGroup
        fields = [
            "name", "comment"
        ]
