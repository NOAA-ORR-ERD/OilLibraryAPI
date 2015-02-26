""" Cornice services.
"""
from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

import unit_conversion as uc

from ..common.views import cors_policy, obj_id_from_url

from oil_library import _get_db_session
from oil_library.models import Oil, ImportedRecord
from oil_library.utilities import get_viscosity

oil_api = Service(name='oil', path='/oil*obj_id',
                  description="List All Oils",  cors_policy=cors_policy)


@oil_api.get()
def get_oils(request):
    session = _get_db_session()
    obj_id = obj_id_from_url(request)

    if not obj_id:
        # Return all oils in JSON format.  We only return the searchable
        # columns.
        oils = session.query(Oil)
        return [{'adios_oil_id': o.imported.adios_oil_id,
                 'name': o.name,
                 'location': o.imported.location,
                 'field_name': o.imported.field_name,
                 'product_type': o.imported.product_type,
                 'oil_class': o.imported.oil_class,
                 'api': o.api,
                 'pour_point': get_pour_point(o),
                 'viscosity': get_oil_viscosity(o),
                 'categories': get_category_paths(o)}
                for o in oils]
    else:
        try:
            oil = (session.query(Oil).join(ImportedRecord)
                   .filter(ImportedRecord.adios_oil_id == obj_id).one())

            return prune_oil_json(oil.tojson())
        except NoResultFound:
            raise HTTPNotFound()


def get_category_paths(oil, sep='-'):
    return [sep.join([c.name for c in get_category_ancestors(cat)])
            for cat in oil.categories]


def get_category_ancestors(category):
    '''
        Here we take a category, which is assumed to be a node
        in a tree structure, and determine the parents of the category
        all the way up to the apex.
    '''
    cat_list = []
    cat_list.append(category)

    while category.parent is not None:
        cat_list.append(category.parent)
        category = category.parent

    cat_list.reverse()
    return cat_list


def get_pour_point(oil):
    return [oil.pour_point_min_k, oil.pour_point_max_k]


def get_oil_viscosity(oil):
    if oil.api >= 0 and len(oil.kvis) > 0:
        return uc.convert('Kinematic Viscosity', 'm^2/s', 'cSt',
                          float(get_viscosity(oil, 273.15 + 38)))
    else:
        return None


def prune_oil_json(oil_json):
    '''
        The tojson() routine recursively includes a bunch of redundant
        content that we don't want to return.  So we will prune it.
    '''
    for c in oil_json['categories']:
        if 'oils' in c:
            del c['oils']

    for c in oil_json['cuts']:
        if 'imported' in c:
            del c['imported']
        if 'oil' in c:
            del c['oil']

    for d in oil_json['densities']:
        if 'imported' in d:
            del d['imported']
        if 'oil' in d:
            del d['oil']

    for k in oil_json['kvis']:
        if 'oil' in k:
            del k['oil']

    for f in oil_json['sara_fractions']:
        if 'oil' in f:
            del f['oil']

    return oil_json
