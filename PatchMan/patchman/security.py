from pyramid.security import Allow, Everyone, Authenticated

class EntryFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, Authenticated, 'add'),
               (Allow, Authenticated, 'edit'),
               (Allow, Authenticated, 'delete'), ]
    
    def __init__(self, request):
        pass
