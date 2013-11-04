from patchman.models import Plate, PlateLog, DBSession
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from webhelpers import paginate
from webhelpers.paginate import Page
import logging
import transaction
from datetime import datetime

log = logging.getLogger(__name__)

@view_config(route_name="log_get", renderer='json')
def list(request):
    s=request.session
    if 'logts' not in s:
        s['logts'] =datetime.min

    query = DBSession.query(PlateLog).join(Plate).filter(PlateLog.timestamp>s['logts']).order_by("logs.id desc").all()

    if len(query):
        s['logts'] = query[0].timestamp

    return query

