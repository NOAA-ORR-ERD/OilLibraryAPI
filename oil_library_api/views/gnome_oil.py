""" Cornice services.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

from ..common.views import cors_policy, obj_id_from_url
from .oil import get_oil_searchable_fields

from oil_library import _get_db_session
from oil_library.models import ImportedRecord, Oil, Category
from oil_library.oil_props import OilProps

gnome_oil_api = Service(name='gnome_oil', path='/gnome_oil*obj_id',
                       description=('Get Gnome Oil from database '),
                       cors_policy=cors_policy)


@gnome_oil_api.get()
def get_gnome_oil(request):
    '''Returns gnome oil for pygnome'''
    session = _get_db_session()
    obj_id = obj_id_from_url(request)

    if not obj_id:
        # Return all oils in JSON format.  We only return the searchable
        # columns.
        return [get_oil_searchable_fields(o) for o in session.query(Oil)]
    else:
        try:
            oil = (session.query(Oil).join(ImportedRecord)
                   .filter(ImportedRecord.adios_oil_id == obj_id).one())

            op = OilProps(oil)
            return op.get_gnome_oil()

        except NoResultFound:
            raise HTTPNotFound()

