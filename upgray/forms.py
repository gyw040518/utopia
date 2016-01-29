# coding:utf-8
from django import forms

from upgray.models import Rule, System

class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = [
            "name", "shortname", "content", "status", "use_default_auth", "is_active", "comment"
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '规则名称'}),
            'shortname': forms.TextInput(attrs={'placeholder': '规则简称'}),
            'content': forms.Textarea(
                attrs={'placeholder': 'name1\nname2'})
        }


class SystemForm(forms.ModelForm):
    class Meta:
        model = System
        fields = [
            "name", "rule_name", "status", "old_version", "new_version", "use_default_auth", "comment"
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '系统名称'}),
            'old_version': forms.Textarea(
                attrs={'placeholder': 'name1\nname2'}),
            'new_version': forms.Textarea(
                attrs={'placeholder': 'name1\nname2'})
        }