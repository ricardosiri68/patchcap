import requests
from ConfigParser import ConfigParser
import json


class Response(object):
	def __init__(self, r):
		self.status = r.status_code
		if r.status_code<400:
			self.result  = r.json()
		else:
			self.result = r.reason
	def error(self):
		return self.status>=400


class Backend(object):

    def __init__(self):
        config = ConfigParser()
        config.read('secret_settings.ini')
        self.user = config.get('backend', 'user')
        self.password = config.get('backend', 'password')
	self.host = config.get('backend', 'host')
        self.client = requests.Session()
        auth = {'username': self.user, 'password': self.password}
        login= self.host + '/users/login/'
        r = self.client.post(login, json=auth)
        self.url_base = self.host + '/devices'

    def add_device(self, dev):
        return self.client.post(self.url_base, json=dev)

    def delete_device(self, id):
        return self.client.delete(self.url_base+'/'+str(id))


    def devices(self, id = None):
        if id:
            url = self.url_base+'/'+str(id)
        else:
            url = self.url_base
        return Response(self.client.get(url))

