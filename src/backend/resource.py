"""
resources for traversal
"""
from . import models as m
from pyramid.security import Allow, Everyone, Authenticated,ALL_PERMISSIONS
from pyramid import security
from pyramid.httpexceptions import HTTPUnauthorized
from  datetime import datetime , timedelta
import uuid
import contextlib
from .mailers import send_email

import logging

@contextlib.contextmanager
def cleanup_rec(rec, session):
    yield rec
    session.delete(rec)
    


class BaseResource(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
               (Allow, Authenticated, 'view'),
               (Allow, 'g:admin', ALL_PERMISSIONS) ]

    def __init__(self, request, name=None, parent=None):
        self.__name__ = name or self.__name__
        self.__parent__ = parent
        self._request = request
        self.__children__ = {}

    def _create_child(self, ChildClass):
        child = ChildClass(self._request, parent=self)
        self.__children__[child.__name__] = child
        return child


    def __getitem__(self, key):
        return self.__children__[str(key).lower()]


class BaseQuery(BaseResource):
    __model__ = None

    def __qry__(self):
        return self._request.db.query(self.__model__)

    def __getitem__(self, key):
        try:
            id = int(key)
        except ValueError:
            raise KeyError("%s(%s) not found" % (self.__model__.__name__, key))

        result = self.__qry__().get(id)

        if result:
            result.__parent__ = self
            return result
        else:
            raise KeyError("%s(%s) not found" % (self.__model__.__name__, key))

    def list(self):
        return self.__qry__().all()

    def delete(self, id):
        return self._request.db.delete(id)


class AlarmContainer(BaseQuery):
    __model__ = m.Alarm
    __name__ = "alarms"
    def create(self, name, plates, class_id):
        Plates = PlateContainer(self._request)
        a = self.__model__()
        a.name = name
        a.alarm_class_id = class_id
        a.plates = []
        for p in plates:
            a.plates.append(Plates.get[p['code']])
        self._request.db.add(a)
        return a


class DeviceContainer(BaseQuery):
    __model__ = m.Device
    __name__ = "devices"

    def create(self, username, roi, name, ip, outstream, password, instream, logging):
        d = self.__model__(name, instream, outstream, ip, username, password, roi, logging)
        self._request.db.add(d)
        return d


class LogContainer(BaseQuery):
    __model__ = m.Log
    __name__ = "logs"
    def create(self, roi, code, ts, conf, device_id):
        l = self.__model__(device_id, ts, roi, code, conf)
        self._request.db.add(l)
        return l


class PlateContainer(BaseQuery):
    __model__ = m.Plate
    __name__ = "plates"

    def create(self, name, alarms):
        Alarms = AlarmContainer(self.request)
        p = self.__model__()
        p.name = name
        p.alarms = []
        for a in alarms:
            p.alarms.append(Alarms[a['id']])
        self._request.db.add(p)
        return p

    def get(self, code):
        p = self._request.db.query(self.__model__).filter_by(code=code).first()
        if not p:
            p = Plate(code)
            self._request.db.add(p)
        return p


class UserContainer(BaseQuery):
    __model__ = m.User
    __name__ = "users"

    CMD_REGISTER = "register"
    CMD_RESET = "forgot"

    def login(self, login_id, password):
        u = self.__qry__().filter_by(username=login_id).first()
        if u and u.password == password:
            headers = security.remember(self._request, u.id)
            self._request.response.headerlist.extend(headers)
        else:
            raise HTTPUnauthorized("login failed")

    def logout(self):
        self._request.response.headerlist.extend(security.forget(self._request))


    def register(self, email):
        cc = self._request.api_root["command"]
        result = cc.get_command(email, self.CMD_REGISTER)
        if not (result and result.expire_on > datetime.now()):
            result = cc.create_command(email, self.CMD_REGISTER)

        activation_link = self._request.route_url("home",
                                                  _anchor="/activate/%s" % result.command_id)
        send_email(self._request.mailer, 
                   email, 
                   self._request.registry.settings['mail_sender'], 
                   "Activate Your Account", 
                   "activate.html", 
                   activation_link=activation_link)


    def activate(self, command_id=None, email=None, password=None):
        cmd = self._request.api_root["command"][command_id]
        if cmd and cmd.identity == email and cmd.command_type == self.CMD_REGISTER:
            with cleanup_rec(cmd, self._request.db) as cmd:
                result = self.__model__(email=email, password=password)
                self._request.db.add(result)
                return result
        else:
            msg = "Invalid %s Command for %s, %s" % \
                  (self.CMD_REGISTER, command_id, email)
            raise ValueError(msg)

    def create(self, username, name, email, password, profiles):
        Profiles = ProfileContainer(self._request)
        u = self.__model__(name=name, username=username, email=email, password=password)
        u.profiles = []
        for p in profiles:
            u.profiles.append(Profiles[p['id']])


        self._request.db.add(u)
        return u


    def request_reset(self, email):
        cc = self._request.api_root["command"]
        result = cc.get_command(email, self.CMD_RESET)
        if not (result and result.expire_on > datetime.now()):
            result = cc.create_command(email, self.CMD_RESET)

        reset_link = self._request.route_url("home",
                                             _anchor="/reset/%s" % result.command_id)
        send_email(self._request.mailer, 
                   email,
                   self._request.registry.settings["mail_sender"],
                   "Reset Your Password",
                   "reset.html",
                   reset_link=reset_link)


    def do_reset(self, command_id=None, email=None, password=None):
        cmd = self._request.api_root["command"][command_id]
        if cmd and cmd.identity == email and cmd.command_type == self.CMD_RESET:
            with cleanup_rec(cmd, self._request.db) as cmd:
                user = self._request.db.query(self.__model__).filter_by(email=email).first()

                user.password = password
                self._request.db.add(user)
                return user



class ProfileContainer(BaseQuery):
    __model__ = m.Profile
    __name__ = "profiles"

    def create(self, name):
        p = self.__model__()
        p.name = name
        self._request.db.add(p)
        return p


class APIRoot(BaseResource):
    def __init__(self, request):
        super(self.__class__, self).__init__(request)
        request.api_root = self
        self._create_child(AlarmContainer)
        self._create_child(DeviceContainer)
        self._create_child(LogContainer)
        self._create_child(ProfileContainer)
        self._create_child(UserContainer)
