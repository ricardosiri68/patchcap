from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from patchman.models import initialize_sql
from patchman.utils.subscribers import add_renderer_globals
from patchman.utils.subscribers import csrf_validation
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from pyramid_beaker import session_factory_from_settings,set_cache_regions_from_settings

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    initialize_sql(settings)
    
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    
    authentication_policy = AuthTktAuthenticationPolicy('somesecret')
    authorization_policy = ACLAuthorizationPolicy()
 
    config = Configurator(
        settings=settings, 
        session_factory=session_factory,
        authentication_policy=authentication_policy,
        authorization_policy=authorization_policy
    )
    
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(csrf_validation, NewRequest)    
    
    # mako settings for file extension .html
    config.include('pyramid_mako')
    config.add_mako_renderer(".html")

    config.add_static_view("static", "patchman:static", cache_max_age=3600)
    
    # home 
    config.add_route("home", "/")
    config.add_route("home_dashboard", "/home/dashboard")
    
    # country routes
    config.add_route("brand_list", "/brands/list")
    config.add_route("brand_search", "/brands/search")
    config.add_route("brand_new", "/brands/new",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("brand_edit", "/brands/{id}/edit",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("brand_delete", "/brands/{id}/delete",
                     factory='patchman.security.EntryFactory'
)
    
   # devices 
    config.add_route("device_list", "/devices/list")
    config.add_route("device_search", "/devices/search")
    config.add_route("device_new", "/devices/new",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("device_view", "/devices/{id}/view")
    config.add_route("device_edit", "/devices/{id}/edit",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("device_delete", "/devices/{id}/delete",
                     factory='patchman.security.EntryFactory'
)

    # patentes routes
    config.add_route("plate_list", "/plates/list")
    config.add_route("plate_search", "/plates/search")
    config.add_route("plate_new", "/plates/new",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("plate_edit", "/plates/{id}/edit",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("plate_delete", "/plates/{id}/delete",
                     factory='patchman.security.EntryFactory'
)
    config.add_route("log_get", "/logs/get")
    
    config.add_route('auth', '/sign/{action}')
    
    config.scan()
    return config.make_wsgi_app()
