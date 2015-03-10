from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from patchman.models import initialize_sql
from patchman.utils.routes import MyRoutes
from pyramid_beaker import session_factory_from_settings,set_cache_regions_from_settings
from pyramid.config import Configurator
from pyramid.events import BeforeRender, NewRequest
from patchman.utils.subscribers import add_renderer_globals, csrf_validation


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
    
    
    config.add_mako_renderer(".html")

    config.add_static_view("static", "patchman:static", cache_max_age=3600)
    
    MyRoutes(config)
      
    config.scan()
    return config.make_wsgi_app()
