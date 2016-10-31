'''
    This is just a scratchpad script I use inside ipython
'''

import oil_library
from oil_library import get_oil, _get_db_session
from oil_library.models import Oil
from oil_library.oil_props import OilProps

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


session = _get_db_session()
print 'Our session:', session.connection().engine

# oil_obj = get_oil('LUCKENBACH FUEL OIL')
oil_obj = get_oil('BAHIA')
props_obj = OilProps(oil_obj)

pp.pprint([f for f in props_obj.component_mass_fractions()])

oil_obj = session.query(Oil).filter(Oil.adios_oil_id == 'AD00584').one()

my_str = oil_obj.imported.comments

print my_str

benz = get_oil(oil_library.sample_oils.benzene.json_data)
print benz
