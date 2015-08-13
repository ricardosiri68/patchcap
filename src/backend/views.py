from pyramid.view import view_config
from . import resource
from . import schemas
import colander
from pyramid.httpexceptions import exception_response
from .mailers import send_email

@view_config(route_name="home", 
             renderer="home.html")
def home_view(request):
    return {}


@view_config(route_name="api", 
             context=resource.UserContainer, 
             name="register", 
             renderer="json", 
             request_method="POST")
def register_view(context, request):
    context.register(schemas.RegisterSchema().deserialize(request.POST)["email"])
    return {}


@view_config(route_name="api", 
             context=resource.UserContainer, 
             name="activate", 
             renderer="json", 
             request_method="POST")
def activate_view(context, request):
    data = schemas.ActivateSchema().deserialize(request.POST)
    new_user = context.activate(**data)
    return dict(email=new_user.email, id=new_user.id)



@view_config(route_name="api",
             context=resource.UserContainer,
             name="forgot",
             renderer="json",
             request_method="POST")
def forgot_view(context, request):
    data = schemas.ForgotSchema().deserialize(request.POST)
    context.request_reset(data["email"])
    return {}


@view_config(route_name="api",
             context=resource.UserContainer,
             name="reset",
             renderer="json",
             request_method="POST")
def reset_view(context, request):
    data = schemas.ResetSchema().deserialize(request.POST)
    user = context.do_reset(**data)
    return dict(email=user.email, id=user.id)

@view_config(route_name="api", 
             context=resource.APIRoot, 
             name="login", 
             renderer="json", 
             request_method="POST")
def login_view(context, request):
    context["user"].login(**schemas.LoginSchema().deserialize(request.POST))
    return {}


@view_config(route_name="api", 
             context=resource.APIRoot, 
             name="logout", 
             renderer="json", 
             request_method="POST")
def logout_view(context, request):
    context["user"].logout()
    return {}


@view_config(route_name="api",
             context=resource.UserContainer,
             name="me",
             renderer="json")
def me_view(context, request):
    u = request.authenticated_user()
    if u:
        return dict(email=u.email, first_name=u.first_name, last_name=u.last_name, id=u.id)
    else:
        raise exception_response(403)


@view_config(context=colander.Invalid, renderer="json")
def validation_error_view(exc, request):
    request.response.status_int = 400
    return exc.asdict()
