""" Cornice services.
"""
import re
import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

from ..common.views import cors_policy, obj_id_from_url

from oil_library import _get_db_session
from oil_library.models import Oil, ImportedRecord
from oil_library.oil_props import OilProps

oil_api = Service(name='oil', path='/oil*obj_id',
                  description="List All Oils",  cors_policy=cors_policy)


logger = logging.getLogger(__name__)


def memoize_oil_arg(func):
    res = {}

    def memoized_func(oil):
        if oil.adios_oil_id not in res:
            logger.info('loading in-memory oil dict.  Key: "{}"'
                        .format(oil.adios_oil_id))
            res[oil.adios_oil_id] = func(oil)

        return res[oil.adios_oil_id]

    return memoized_func


@oil_api.get()
def get_oils(request):
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

            return prune_oil_json(oil.tojson())
        except NoResultFound:
            raise HTTPNotFound()


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    return {'adios_oil_id': oil.imported.adios_oil_id,
            'name': oil.name,
            'location': oil.imported.location,
            'field_name': oil.imported.field_name,
            'product_type': oil.imported.product_type,
            'oil_class': oil.imported.oil_class,
            'api': oil.api,
            'pour_point': get_pour_point(oil),
            'viscosity': get_oil_viscosity(oil),
            'categories': get_category_paths(oil),
            'categories_str': get_category_paths_str(oil),
            'synonyms': get_synonyms(oil),
            'quality_index': oil.quality_index
            }


def get_category_paths(oil, sep='-'):
    return [sep.join([c.name for c in get_category_ancestors(cat)])
            for cat in oil.categories]


def get_category_paths_str(oil, sep='-'):
    regex = re.compile(r'\b(Crude-|Refined-)\b')
    cat_str = ','.join(sorted(set(get_category_paths(oil))))
    return regex.sub("", cat_str)


def get_synonyms(oil, sep=','):
    syn_list = [s.name for s in oil.imported.synonyms]
    return ','.join(syn_list)


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
        oil_props = OilProps(oil)
        return oil_props.kvis_at_temp(273.15 + 38)
    else:
        return None


def prune_oil_json(oil_json):
    '''
        The tojson() routine recursively includes a bunch of redundant
        content that we don't want to return.  So we will prune it.
    '''
    for oil_attr_name in ('categories', 'cuts', 'densities', 'kvis',
                          'sara_fractions', 'sara_densities',
                          'molecular_weights'):
        for oil_attr in oil_json[oil_attr_name]:
            for attr_name in ('imported', 'oils', 'oil', 'oil_id'):
                if attr_name in oil_attr:
                    del oil_attr[attr_name]

    del oil_json['imported']['oil']
    del oil_json['estimated']['oil']

    return oil_json
