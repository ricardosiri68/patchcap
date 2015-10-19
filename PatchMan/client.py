import requests
from ConfigParser import ConfigParser


class Backend(object):

    def __init__(self):
        config = ConfigParser()
        config.read('secret_settings.ini')
        self.user = config.get('backend', 'user')
        self.password = config.get('backend', 'password')
        self.client = requests.Session()
        auth = {'username': 'hernando', 'password': 'nonsecurepass'}
        login="http://localhost:8080/api/users/login/"
        r = self.client.post(login, json=auth)
        self.url_base ='http://localhost:8080/api/devices'

    def add_device(self, dev):
        return self.client.post(self.url_base, json=dev)

    def delete_device(self, id):
        return self.client.delete(self.url_base+'/'+str(id))


    def devices(self, id = None):
        if id:
            url = self.url_base+'/'+str(id)
        else:
            url = self.url_base
        r = self.client.get(url)
        return r.json()

