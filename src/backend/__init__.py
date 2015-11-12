from pyramid.events import NewRequest
from pyramid.config import Configurator
from pyramid import authentication, authorization

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from .resource import APIRoot 
from .security import groupfinder, get_user
from .models import User
from ConfigParser import ConfigParser
import logging
import locale

log = logging.getLogger(__name__)

def db(request):
    """every request will have a session associated with it. and will
    automatically rollback if there's any exception in dealing with
    the request
    """
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()

    request.add_finished_callback(cleanup)

    return session

def config_static(config):
    config.add_static_view('app', 'navigation-app', cache_max_age=3600)

def config_jinja2(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path('templates', name='.html')

def localization(request):
    locale.setlocale(locale.LC_ALL, 'es_AR.utf8')
    return 'es'

def config_mailer(config):
    config.include('pyramid_marrowmailer')
    config.include('pyramid_tm')

def config_db(config, settings):
    # configure database with variables sqlalchemy.*
    engine = engine_from_config(settings, prefix="sqlalchemy.")
    config.registry.dbmaker = sessionmaker(bind=engine)

    # add db session to request
    config.add_request_method(db, reify=True)


def config_routes(config):
    config.add_route('home', '/')
    config.scan()
    config.add_route("api", '/api/*traverse', factory=APIRoot)
    config.add_route('socket.io', 'socket.io/*remaining'),


def config_auth_policy(config, settings):
    policy = authentication.AuthTktAuthenticationPolicy(
            settings['auth_secret'], 
            groupfinder, 
            cookie_name="backend_auth", 
            hashalg="sha512" #, 
            # timeout = 20, 
            #reissue_time=2
            )
    config.set_authentication_policy(policy)
    config.set_authorization_policy(authorization.ACLAuthorizationPolicy())
    config.set_default_permission('view')
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*' if request.method=='OPTIONS' or not 'Host' in request.headers else request.headers.get('Host'),
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)


def config_secrets(settings):
    if "secrets" in settings:
        try:
            config = ConfigParser()
            config.read(settings["secrets"])
            settings.update(config.items("secrets"))
        except:
            log.warn("secrets were specificed in the configuration but could not be read\n\n%s" % settings.get("secrets", ""), exc_info=1)

def main(global_config, **settings):
    config_secrets(settings)
    config = Configurator(settings=settings)
    config_static(config)
    config_jinja2(config)
    config_db(config, settings)
    config_routes(config)
    config_auth_policy(config, settings)
    config.set_locale_negotiator(localization)
    config_mailer(config)
    config.add_request_method(get_user,'user', reify=True)
    return config.make_wsgi_app()
