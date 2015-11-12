import gevent
from pyramid import security
from pyramid.httpexceptions import exception_response
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from . import resource
from . import schemas
import colander
from .mailers import send_email
from models import Device, User, Profile, Plate, Alarm
from zope.sqlalchemy import mark_changed
import datetime
import logging
import transaction
import json

log = logging.getLogger(__name__) 

@view_config(route_name="home", renderer="navigation-app/index.html", permission=security.NO_PERMISSION_REQUIRED)
def home_view(request):
    return {}

@view_defaults(route_name='api', renderer='json')
class RestView(object):
    __serializer__ = None

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(request_method="OPTIONS")
    def options_view(self):
        return Response(status_int=200) 

    def __delete__(self):
        if self.context is None:
            raise HTTPNotFound()

        self.request.db.delete(self.context)
        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

    def __list__(self):
        r = self.context.list()
        if r is None:
            raise HTTPNotFound()
        else:
            elements = []
            for e in r:
                elements.append(__serializer__.serialize(__serializer__.dictify(e)))
            return elements

    def __create__(self):
        data = schemas.DeviceSchema.deserialize(self.request.json_body)
        r = self.context.create(**data)
        return Response(
            status='201 Created',
            content_type='application/json; charset=UTF-8')

    def __read__(self):
        r = self.context
        if r is None:
            raise HTTPNotFound()
        else:
            self.request.response.headers['Vary'] = 'Accept-Encoding'
            self.request.response.headers['X-Content-Type-Options'] = 'nosniff'
            self.request.response.headers['Content-Type'] = 'application/json'
            del self.request.response.headers['Content-Type']
            return __serializer__.serialize(r.__dict__)


class DeviceView(RestView):
    __serializer__ = schemas.DeviceSchema
    @view_config(request_method='POST', context = resource.DeviceContainer, permission="add")
    def create(self):
        return self.__create__()

    @view_config(request_method='GET', context=Device)
    def read(self):
           return self.__read()

    @view_config(request_method='GET', context = resource.DeviceContainer)
    def list(self):
        return self.__list__()


    @view_config(request_method='PUT', context=Device)
    def update(self):
        device = self.context
        if device is None:
            raise HTTPNotFound()
        else:
            data = schemas.DeviceSchema.deserialize(self.request.json_body)
            device.name = data['name']
            device.instream = data['instream']
            device.outstream = data['outstream']
            device.ip = data['ip']
            device.username = data['username']
            device.password = data['password']
            device.roi = data['roi']
            device.logging = data['logging']
            self.request.db.add(device)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')


    @view_config(request_method='DELETE', context=Device)
    def delete(self):
        return self.__delete__()

    @view_config(name="log", request_method="POST", permission=security.NO_PERMISSION_REQUIRED)
    def log_view(self):
        data = schemas.LogSchema().deserialize(self.request.json_body)
        self.context.log(data['device_id'], data['ts'], data['roi'], data['code'], data['conf'])
        return {}


class UserView(RestView):
    __serializer__ = schemas.UserSchema
    @view_config(request_method='POST', context = resource.UserContainer)
    def create(self):
        return self.__create__()

    @view_config(request_method='GET', context = resource.UserContainer)
    def list(self):
        return self.__list__()

    @view_config(request_method='GET', context=User)
    def read(self):
        return self.__read__()

    @view_config(request_method='PUT', context=User)
    def update(self):
        profiles = resource.ProfileContainer(self.request)
        user = self.context
        if user is None:
            raise HTTPNotFound()
            
        data = schemas.UserSchema.deserialize(self.request.json_body)
        user.name = data['name']
        user.email = data['email']
        user.username = data['username']
        if data['password']:
            user.password = data['password']
        
        user.profiles = []
        for p in data['profiles']:
            user.profiles.append(profiles[p['id']])

        self.request.db.add(user)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')


    @view_config(request_method='DELETE', context=User)
    def delete(self):
        if self.context.id!=1:
            return self.__delete__()
        raise HTTPNotFound()

    @view_config(name="login", request_method="POST", permission=security.NO_PERMISSION_REQUIRED)
    def login_view(self):
        data = schemas.LoginSchema().deserialize(self.request.json_body)
        self.context.login(data['username'], data['password'])
        return {}

    @view_config(name="logout")
    def logout_view(self):
        self.context.logout()
        return {}

    @view_config(name="me")
    def me_view(self):
        u = self.request.user
        if u:
            return dict(email=u.email, name=u.name, username=u.username, id=u.id)
        else:
            raise exception_response(403)

    @view_config(name="forgot", request_method="POST")
    def forgot_view(self):
        data = schemas.ForgotSchema().deserialize(request.POST)
        context.request_reset(data["email"])
        return {}

    @view_config(name="reset", request_method="POST")
    def reset_view(context, request):
        data = schemas.ResetSchema().deserialize(request.POST)
        user = context.do_reset(**data)
        return dict(email=user.email, id=user.id)


class ProfileView(RestView):
    __serializer__ = schemas.ProfileSchema
    @view_config(request_method='POST', context = resource.ProfileContainer, permission="add")
    def create(self):
        return self.__create__()

    @view_config(request_method='GET', context = resource.ProfileContainer)
    def list(self):
        return self.__list__()

    @view_config(request_method='GET', context=Profile)
    def read(self):
        return sel.__read__() 

    @view_config(request_method='PUT', context=Profile)
    def update(self):
        p = self.context
        if p is None:
            raise HTTPNotFound()
        else:
            data = __serializer__.deserialize(self.request.json_body)
            p.name = data['name']
            self.request.db.add(p)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

    @view_config(request_method='DELETE', context=Profile)
    def delete(self):
        return self.__delete__()


class PlateView(RestView):
    __serializer__ = schemas.PlateSchema
    @view_config(request_method='POST', context = resource.PlateContainer, permission="add")
    def create(self):
        return self.__create__()

    @view_config(request_method='GET', context = resource.PlateContainer)
    def list(self):
        return self.__list__()

    @view_config(request_method='GET', context=Plate)
    def read(self):
        return self.__read__() 

    @view_config(request_method='PUT', context=Plate)
    def update(self):
        p = self.context
        if p is None:
            raise HTTPNotFound()
        else:
            data = __serializer__.deserialize(self.request.json_body)
            p.name = data['name']
            self.request.db.add(p)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

    @view_config(request_method='DELETE', context=Plate)
    def delete(self):
        return self.__delete__()


class AlarmView(RestView):
    __serializer__ = schemas.AlarmSchema
    @view_config(request_method='POST', context = resource.AlarmContainer, permission="add")
    def create(self):
        return self.__create__()

    @view_config(request_method='GET', context = resource.AlarmContainer)
    def list(self):
        return self.__list__()

    @view_config(request_method='GET', context=Alarm)
    def read(self):
        return self.__read__() 

    @view_config(request_method='PUT', context=Alarm)
    def update(self):
        p = self.context
        if p is None:
            raise HTTPNotFound()
        else:
            data = __serializer__.deserialize(self.request.json_body)
            p.name = data['name']
            self.request.db.add(p)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

    @view_config(request_method='DELETE', context=Alarm)
    def delete(self):
        return self.__delete__()


@view_config(context=colander.Invalid, renderer="json",permission=security.NO_PERMISSION_REQUIRED)
def validation_error_view(exc, request):
    request.response.status_int = 400
    return exc.asdict()


@view_config(route_name="socket.io",permission=security.NO_PERMISSION_REQUIRED)
def socketio_service(request):
    r = socketio_manage(request.environ, {'/log': LogNamespace},
                    request)
    return Response(r)


class ClientRoomsMixin(BroadcastMixin):
    def __init__(self, *args, **kwargs):
        super(ClientRoomsMixin, self).__init__(*args, **kwargs)
        if 'rooms' not in self.session:
            self.session['rooms'] = set()

    def join(self, room):
        self.session['rooms'].add(self._get_room_name(room))

    def leave(self, room):
        self.session['rooms'].remove(self._get_room_name(room))

    def _get_room_name(self, room):
        return self.ns_name + '_' + room

    def emit_to_room(self, room, event, *args):
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)
        room_name = self._get_room_name(room)
        for sessid, socket in self.socket.server.sockets.iteritems():
            if 'rooms' not in socket.session:
                continue
            if room_name in socket.session['rooms']:
                socket.send_packet(pkt)


class LogNamespace(BaseNamespace, ClientRoomsMixin):

    _clients = {}
    _running = False

    def initialize(self):
        log.debug('iniciando name. %s', self._running)

    def show_clients(self):
        for k in self._clients:
            log.debug('queda client %s con %s',k, len(self._clients[k]))

    def on_register(self, state):
        log.debug(state)


    def register(self, user_id):
        if user_id not in self._clients:
            self._clients[user_id] = []

        self._clients[user_id].append(id(self))
        log.debug('joining client %s to room %s',id(self), user_id)
        self.join(str(user_id))
        self.show_clients()
        self.session['user_id'] = user_id



    def recv_connect(self):
        if self.request.user:
            user_id = self.request.user.id
        else:
            user_id = 0
            log.info('connecting anonymous')
        self.register(str(user_id))
    
        def senddata():
            user_id = int(self.session['user_id'])
            lastrefresh = {}
            db = self.request.db
            serializer = schemas.LogSchema
            while True:
                devices = User.findBy(user_id).devices if user_id else db.query(Device).all()
                for d in devices:
                    if d.id not in lastrefresh:
                        lastrefresh[d.id] = datetime.datetime(2010, 1, 1, 0, 0, 0)
                    if not d.timestamp() or d.timestamp()<=lastrefresh[d.id]:
                        continue
                    logs = d.logsfrom(lastrefresh[d.id])
                    for l in logs:
                        data = serializer.serialize(serializer.dictify(l))
                        self.emit_to_room(str(user_id), 'refresh',d.id , {'log':data,'t':json.dumps(d.timestamp(), default=deftime)})
                    lastrefresh[d.id] = d.timestamp()
                transaction.commit()
                gevent.sleep(1)
        self.spawn(senddata)


    def recv_disconnect(self):
        user_id = self.session['user_id']
        self._clients[user_id].remove(id(self))
        if not self._clients[user_id]:
            del self._clients[user_id]
        self.disconnect(silent=True)


def deftime(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
 
