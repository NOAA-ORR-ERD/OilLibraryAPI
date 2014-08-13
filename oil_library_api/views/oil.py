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
    return [{'name': o.name,
             'adios_oil_id': o.adios_oil_id,
             'api': o.api,
             'location': o.location,
             'field_name': o.field_name,
             'product_type': o.product_type,
             'oil_class': o.oil_class}
            for o in oils]
