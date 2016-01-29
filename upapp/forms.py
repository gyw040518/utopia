# coding:utf-8
from django import forms

from upapp.models import App, AppGroup
from upapp.models import Map

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = [
            "name", "group", "status", "use_default_auth", "app_type", "is_active", "comment"
        ]


class AppGroupForm(forms.ModelForm):
    class Meta:
        model = AppGroup
        fields = [
            "name", "comment"
        ]

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = [
            "name", "node_ip", "group", "node", "path", "contextroot", "use_default_auth", "map_envs", "comment"
        ]
