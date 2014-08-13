""" Cornice services.
"""
from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

from ..models import DBSession
from oil_library.models import Oil

oil_api = Service(name='oil', path='/oil*obj_id', description="List All Oils")


@oil_api.get()
def get_oils(request):
    '''Returns all oils in JSON format'''
    obj_id = obj_id_from_url(request)

    if not obj_id:
        oils = DBSession.query(Oil)
        return [{'name': o.name,
                 'adios_oil_id': o.adios_oil_id,
                 'api': o.api,
                 'location': o.location,
                 'field_name': o.field_name,
                 'product_type': o.product_type,
                 'oil_class': o.oil_class}
                for o in oils]
    else:
        try:
            oil = (DBSession.query(Oil)
                   .filter(Oil.adios_oil_id == obj_id).one())
            return oil.tojson()
        except NoResultFound:
            raise HTTPNotFound()


def obj_id_from_url(request):
    # the pyramid URL parser returns a tuple of 0 or more
    # matching items, at least when using the * wild card
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None
