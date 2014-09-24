'''
    This is just a scratchpad script I use inside ipython
'''
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import numpy

import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.orm.relationships import (RelationshipProperty,
                                          ONETOMANY)

from pyramid.paster import (get_appsettings,
                            setup_logging)

from oil_library_api.models import DBSession
from oil_library.models import (Base, Oil, Toxicity, Category, Estimated)
from oil_library.oil_props import OilProps

config_uri = 'development.ini'
settings = get_appsettings(config_uri,
                           name='oil_library_api')
engine = engine_from_config(settings, 'sqlalchemy.')
DBSession.configure(bind=engine)
Base.metadata.create_all(engine)

session = DBSession()

oil_obj = session.query(Oil).filter(Oil.adios_oil_id == 'AD00084').one()
oil_props = OilProps(oil_obj, 273.15 + 38)
print oil_props.viscosities
