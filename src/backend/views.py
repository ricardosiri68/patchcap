from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from . import resource
from . import schemas
import colander
from pyramid.httpexceptions import exception_response
from .mailers import send_email
from models import Device, User

@view_config(route_name="home", renderer="home.html")
def home_view(request):
    return {}

@view_defaults(route_name='api', context = resource.DeviceContainer, renderer='json')
class DeviceView(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(request_method='POST')
    def create(self):
        data = schemas.DeviceSchema.deserialize(self.request.json_body)
        r = self.context.create(**data)
        return Response(
            status='201 Created',
            content_type='application/json; charset=UTF-8')

    @view_config(request_method='GET')
    def list(self):
        r = self.context.list()
        if r is None:
            raise HTTPNotFound()
        else:
            devices = []
            for d in r:
                devices.append(schemas.DeviceSchema.serialize(d.__dict__))
            return devices

    @view_config(request_method='GET', context=Device)
    def read(self):
        r = self.context
        if r is None:
            raise HTTPNotFound()
        else:
            self.request.response.headers['Vary'] = 'Accept-Encoding'
            self.request.response.headers['X-Content-Type-Options'] = 'nosniff'
            self.request.response.headers['Content-Type'] = 'application/json'
            del self.request.response.headers['Content-Type'] 
            return schemas.DeviceSchema.serialize(r.__dict__)


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
        if self.context is None:
            raise HTTPNotFound()
        
        self.request.db.delete(self.context)
        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')


@view_defaults(route_name='api', context = resource.UserContainer, renderer='json')
class UserView(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(request_method='POST')
    def create(self):
        data = schemas.UserSchema.deserialize(self.request.json_body)
        r = self.context.create(**data)
        return Response(
            status='201 Created',
            content_type='application/json; charset=UTF-8')

    @view_config(request_method='GET')
    def list(self):
        r = self.context.list()
        if r is None:
            raise HTTPNotFound()
        else:
            users = []
            for u in r:
                users.append(schemas.UserSchema.serialize(u.__dict__))
            return users

    @view_config(request_method='GET', context=User)
    def read(self):
        u = self.context
        if u is None:
            raise HTTPNotFound()
        return schemas.UserSchema.serialize(u.__dict__)


    @view_config(request_method='PUT', context=User)
    def update(self):
        user = self.context
        if user is None:
            raise HTTPNotFound()
            
        data = schemas.UserSchema.deserialize(self.request.json_body)
        user.name = data['name']
        user.email = data['email']
        user.username = data['username']
        user.password = data['password']
            
        self.request.db.add(user)

        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')


    @view_config(request_method='DELETE', context=User)
    def delete(self):
        if self.context is None or self.context.id==1:
            raise HTTPNotFound()
        
        self.request.db.delete(self.context)
        return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

    @view_config(name="forgot", request_method="POST")
    def forgot_view(context, request):
        data = schemas.ForgotSchema().deserialize(request.POST)
        context.request_reset(data["email"])
        return {}


    @view_config(name="reset", request_method="POST")
    def reset_view(context, request):
        data = schemas.ResetSchema().deserialize(request.POST)
        user = context.do_reset(**data)
        return dict(email=user.email, id=user.id)

    @view_config(context=resource.APIRoot, name="login", request_method="POST")
    def login_view(context, request):
        context["user"].login(**schemas.LoginSchema().deserialize(request.POST))
        return {}


    @view_config(context=resource.APIRoot, name="logout", request_method="POST")
    def logout_view(context, request):
        context["user"].logout()
        return {}


    @view_config(name="me")
    def me_view(context, request):
        u = request.authenticated_user()
        if u:
            return dict(email=u.email, name=u.name, username=u.username, id=u.id)
        else:
            raise exception_response(403)


@view_config(context=colander.Invalid, renderer="json")
def validation_error_view(exc, request):
    request.response.status_int = 400
    return exc.asdict()



