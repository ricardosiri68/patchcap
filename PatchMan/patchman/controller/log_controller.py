from patchman.models import Plate, PlateLog, DBSession
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from webhelpers import paginate
from webhelpers.paginate import Page
import logging
import transaction

log = logging.getLogger(__name__)

class Log(object):
    def __init__(self, t, p):
        self.t = t.isoformat()
        self.p = p
    
@view_config(route_name="log_get", renderer='json')
def list(request):
    query = DBSession.query(PlateLog).order_by("id desc").all()
    return query 

