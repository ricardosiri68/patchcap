"""
resources for traversal
"""
from . import models as m
from pyramid import security
from pyramid.httpexceptions import HTTPUnauthorized
from  datetime import datetime , timedelta
import uuid
import contextlib
from .mailers import send_email


@contextlib.contextmanager
def cleanup_rec(rec, session):
    yield rec
    session.delete(rec)
    


class BaseResource(object):
    __name__ = None
    __parent__ = None

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

        result.__parent__ = self

        if result:
            return result
        else:
            raise KeyError("%s(%s) not found" % (self.__model__.__name__, key))


class UserContainer(BaseQuery):
    __model__ = m.User
    __name__ = "user"

    CMD_REGISTER = "register"
    CMD_RESET = "forgot"

    def login(self, login_id, password):
        u = self.__qry__().filter_by(email=login_id).first()
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



class CommandContainer(BaseQuery):
    __model__ = m.Command
    __name__ = "command"

    def __getitem__(self, key):
        result = self.__qry__().filter_by(command_id=key).filter(
            self.__model__.expire_on > datetime.now()
        ).order_by(-self.__model__.created_on).first()
        if result:
            return result
        else:
            raise KeyError("%s(%s) not found or expired" % \
                           (self.__model__.__name__, key))


    def get_command(self, identity, command_type):
        return self.__qry__().filter_by(identity=identity, 
                                        command_type=command_type
        ).order_by(-self.__model__.created_on
        ).filter(self.__model__.expire_on < datetime.now()).first()

    def create_command(self, identity, command_type, **command_args):
        expire_on = datetime.now() + timedelta(days=30)
        result = self.__model__(identity=identity, 
                                command_type=command_type, 
                                command_id=str(uuid.uuid4()), 
                                expire_on=expire_on,
                                **command_args)
        self._request.db.add(result)
        return result

        
class APIRoot(BaseResource):
    def __init__(self, request):
        super(self.__class__, self).__init__(request)
        request.api_root = self
        self._create_child(UserContainer)
        self._create_child(CommandContainer)
