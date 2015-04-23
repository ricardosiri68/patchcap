from patchman.utils import helpers
from pyramid.httpexceptions import HTTPForbidden

def add_renderer_globals(event):
    """ add helpers """
    event['h'] = helpers  

def csrf_validation(event):
    if event.request.method == "POST":
        token = event.request.POST.get("_authentication_token")
        if token is None or token != event.request.session.get_csrf_token():
            raise HTTPForbidden('CSRF token is missing or invalid')
