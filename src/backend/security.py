"""
authentication policy/authorization policy
"""
from . import models as m 
from pyramid import security


def get_principals(user_id, request):
    """
    called by authentication policy
    """
    u = request.db.query(m.User).filter_by(id=int(user_id)).first()

    if u:
        return [u, security.Authenticated]
    else:
        return []
