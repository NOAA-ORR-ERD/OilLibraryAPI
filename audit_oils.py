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
from oil_library.models import Base, Oil, Toxicity, Category
from oil_library.oil_props import OilProps

session = DBSession()

for n in range(20, 31, 1):
    print
    adios_id = 'AD{:>05}'.format(n)
    print adios_id
    try:
        oilobj = (session.query(Oil)
                  .filter(Oil.adios_oil_id == adios_id)
                  .one())
    except:
        print 'not found. continue...'
        continue

    oil_props = OilProps(oilobj)

    print oil_props.viscosity

oilobj = (session.query(Oil)
          .filter(Oil.name == 'FUEL OIL NO.6')
          .one())

print oilobj
oil_props = OilProps(oilobj)

pp.pprint(oil_props.viscosities)
print 'pour point (min, max): ', (oil_props._r_oil.pour_point_min,
                                  oil_props._r_oil.pour_point_max)

for t in numpy.linspace(275.0, 325.0, 12.0):
    oil_props.temperature = t
    print '{0} at {1}'.format(
                              oil_props.viscosity,
                              t
                              )
