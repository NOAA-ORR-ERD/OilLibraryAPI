""" Cornice services.
"""
from cornice import Service

from ..models import DBSession
from oil_library.models import Oil

oil_api = Service(name='oil', path='/oil', description="List All Oils")


@oil_api.get()
def get_oils(request):
    '''Returns all oils in JSON format'''
    oils = DBSession.query(Oil)
    return [o.tojson() for o in oils]
