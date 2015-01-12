'''
    This is just a scratchpad script I use inside ipython
'''
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from collections import defaultdict
from math import log, exp

import numpy
np = numpy

import transaction

import unit_conversion as uc

from sqlalchemy import engine_from_config
from sqlalchemy.orm.relationships import (RelationshipProperty,
                                          ONETOMANY)

from pyramid.paster import (get_appsettings,
                            setup_logging)

from oil_library_api.models import DBSession
from oil_library.models import (Base, ImportedRecord, Oil,
                                Density, Toxicity, Category)
from oil_library.oil_props import OilProps

from oil_library.utilities import get_viscosity, get_boiling_points_from_api

config_uri = 'development.ini'
settings = get_appsettings(config_uri,
                           name='oil_library_api')
engine = engine_from_config(settings, 'sqlalchemy.')
DBSession.configure(bind=engine)
Base.metadata.create_all(engine)

session = DBSession()

oil_obj = session.query(Oil).filter(Oil.name == 'ALASKA NORTH SLOPE').one()
props_obj = OilProps(oil_obj)

viscosity = uc.convert('Kinematic Viscosity', 'm^2/s', 'cSt',
                       get_viscosity(oil_obj, 273.15 + 38))

print oil_obj, '\n\tviscosity at 38C =', viscosity
for v in oil_obj.kvis:
    v_ref, t_ref = v.m_2_s, v.ref_temp_k
    print '\tviscosity: {0} m^2/s at {1}K'.format(v.m_2_s, v.ref_temp_k)
print 'imported pour points:', (oil_obj.imported.pour_point_min_k,
                                oil_obj.imported.pour_point_max_k)
print 'oil pour points:', (oil_obj.pour_point_min_k,
                           oil_obj.pour_point_max_k)


def get_ptry_values(oil_obj, watson_factor, fraction_of_cut=0.5):
    previous_cut_fraction = 0.0
    for c in oil_obj.cuts:
        T_i = c.vapor_temp_k

        F_i = c.fraction - previous_cut_fraction
        previous_cut_fraction = c.fraction

        P_try = 1000 * (T_i ** (1.0 / 3.0) / watson_factor)
        yield (P_try, F_i * fraction_of_cut, T_i)

mass_left = 1.0
if oil_obj.imported.resins:
    mass_left -= oil_obj.imported.resins

if oil_obj.imported.asphaltene_content:
    mass_left -= oil_obj.imported.asphaltene_content
api = oil_obj.imported.api

print 'boiling points from api:'
pp.pprint(get_boiling_points_from_api(5, mass_left, api))

print 'summed boiling point fractions'
summed_boiling_points = []
for t, f in get_boiling_points_from_api(5, mass_left, api):
    added = False
    for idx, [ut, summed] in enumerate(summed_boiling_points):
        if np.isclose(t, ut):
            summed_boiling_points[idx][1] += f
            added = True
            break
    if added is False:
        summed_boiling_points.append([t, f])
pp.pprint(summed_boiling_points)

print 'oil cuts:'
pp.pprint(oil_obj.cuts)
print 'oil resins:', oil_obj.imported.resins
print 'oil aspaltenes:', oil_obj.imported.asphaltene_content

print 'oil imported cuts =', oil_obj.imported.cuts

print '\ntrial densities:'
K_arom = 10.0
K_sat = 12.0
for r in get_ptry_values(oil_obj, K_arom):
    print '\t', r

for r in get_ptry_values(oil_obj, K_sat):
    print '\t', r

for f in oil_obj.sara_fractions:
    if f.sara_type in ('Resins', 'Asphaltenes'):
        print '\t', (1100.0, f.fraction)

print '\naverage density based on trials:'
print sum([(P_try * F_i)
           for P_try, F_i, T_i in get_ptry_values(oil_obj, K_arom)] +
          [(P_try * F_i)
           for P_try, F_i, T_i in get_ptry_values(oil_obj, K_sat)] +
          [(1100.0 * f.fraction) for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')]
          )

print 'Now try to get saturate/aromatic mass fractions based on trials'

print '\noil sara fractions:'
print sum([f.fraction for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')])

print '\noil densities'
print oil_obj.densities




