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


def get_ptry_values(oil_obj, watson_factor, sub_fraction=None):
    previous_cut_fraction = 0.0
    for idx, c in enumerate(oil_obj.cuts):
        T_i = c.vapor_temp_k

        F_i = c.fraction - previous_cut_fraction
        previous_cut_fraction = c.fraction

        P_try = 1000 * (T_i ** (1.0 / 3.0) / watson_factor)

        if sub_fraction is not None and len(sub_fraction) > idx:
            print '(f, sub_f):', F_i, sub_fraction[idx]
            F_i = sub_fraction[idx]

        yield (P_try, F_i, T_i)

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
ptry_values = ([v for v in get_ptry_values(oil_obj, K_arom)] +
               [v for v in get_ptry_values(oil_obj, K_sat)])

for r in ptry_values:
    print '\t', r

for f in oil_obj.sara_fractions:
    if f.sara_type in ('Resins', 'Asphaltenes'):
        print '\t', (1100.0, f.fraction)

print '\naverage density based on trials assuming equal sub-fractions:'
print sum([(P_try * (F_i * 0.5))
           for P_try, F_i, T_i in ptry_values] +
          [(1100.0 * f.fraction) for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')]
          )

print '\nNow try to get saturate/aromatic mass fractions based on trials'
print 'molecular weights:'
for mw in oil_obj.molecular_weights:
    print '\t', (mw.saturate, mw.aromatic, mw.ref_temp_k)

sa_ratios = []
for P_try, F_i, T_i in get_ptry_values(oil_obj, K_sat):
    if T_i < 530.0:
        sg = P_try / 1000
        mw = None
        for v in oil_obj.molecular_weights:
            if np.isclose(v.ref_temp_k, T_i):
                mw = v.saturate
                break

        if mw is not None:
            print '(F_i, sg, mw) =', (F_i, sg, mw)
            f_sat = F_i * (2.2843 - 1.98138 * sg - 0.009108 * mw)
            print 'initial f_sat:', f_sat

            if f_sat >= F_i:
                f_sat = F_i
            elif f_sat < 0:
                f_sat = 0

            f_arom = F_i * (1 - f_sat)

            print '(f_sat, f_arom) =', (f_sat, f_arom)
            sa_ratios.append((f_sat, f_arom))
        else:
            print '\tNo molecular weight at that temperature.'
    else:
        f_sat = f_arom = F_i / 2
        print '(f_sat, f_arom) =', (f_sat, f_arom)
        sa_ratios.append((f_sat, f_arom))

print '\naverage density based on trials using adjusted fractions:'
ptry_values = ([v for v in get_ptry_values(oil_obj, K_sat,
                                           [r[0] for r in sa_ratios])] +
               [v for v in get_ptry_values(oil_obj, K_arom,
                                           [r[1] for r in sa_ratios])])

print 'ptry_values:'
pp.pprint(ptry_values)
print 'sum of fractions:', sum([F_i for P_try, F_i, T_i in ptry_values])
print sum([(P_try * F_i)
           for P_try, F_i, T_i in ptry_values] +
          [(1100.0 * f.fraction) for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')]
          )


print '\noil sara fractions:'
print sum([f.fraction for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')])

print '\noil densities'
print oil_obj.densities












