#coding=utf-8

import urllib2, urllib, json, re
from utopia.settings import *
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class saltApi:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(BASE_DIR, 'utopia.conf'))
        self.__url = 'https://' + SALT_HOST + ':' + SALT_PORT
        self.__user = SALT_USER
        self.__password = SALT_PASSWD
        self.__token_id = self.salt_login()

    def salt_login(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token':''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError

    def postRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content['return']

    def saltCmd(self, params):
        obj = urllib.urlencode(params)
        obj, number = re.subn("arg\d", 'arg', obj)
        res = self.postRequest(obj)
        return res