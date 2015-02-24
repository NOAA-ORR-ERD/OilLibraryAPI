""" Cornice services.
"""
from cornice import Service

from ..common.views import cors_policy

from oil_library import _get_db_session
from oil_library.models import ImportedRecord, Oil, Category

distinct_api = Service(name='distinct', path='/distinct',
                       description=('List the distinct values of the '
                                    'searchable fields in the Oil database'),
                       cors_policy=cors_policy)


@distinct_api.get()
def get_distinct(request):
    '''Returns all oils in JSON format'''
    session = _get_db_session()

    res = []

    attrs = ('location',
             'field_name')
    for a in attrs:
        values = [r[0] for r in (session.query(getattr(ImportedRecord, a))
                                 .distinct().all())]
        res.append(dict(column=a, values=values))

    categories = dict([(c.name, [child.name for child in c.children])
                       for c in (session.query(Category)
                                 .filter(Category.parent == None))
                       ])
    res.append(dict(column='product_type', values=categories))

    return res
