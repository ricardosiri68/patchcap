"""
authentication policy/authorization policy
"""
from . import models as m
from pyramid.security import authenticated_userid

def _find_user(request, id):
    return request.db.query(m.User).get(id)


def groupfinder(userid, request):
    user = _find_user(request, userid)
    return ['g:'+r.name for r in user.profiles]


def get_user(request):
    userid = authenticated_userid(request)
    if userid is not None:
        return _find_user(request, userid)
    return None
