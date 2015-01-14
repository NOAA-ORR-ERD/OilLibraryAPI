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
    '''
        This gives an initial trial estimate for each density component.

        In theory the fractionally weighted average of these densities,
        combined with the fractionally weighted average resin and asphaltene
        densities, should match the measured total oil density.

        :param oil_obj: an oil database object
        :param watson_factor: The characterization factor originally defined
                              by Watson et al. of the Universal Oil Products
                              in the mid 1930's
                              (Reference: CPPF, section 2.1.15 )
        :param sub_fraction: a list of fractions to be used in lieu of the
                             calculated cut fractions in the database.
    '''
    previous_cut_fraction = 0.0
    for idx, c in enumerate(oil_obj.cuts):
        T_i = c.vapor_temp_k

        F_i = c.fraction - previous_cut_fraction
        previous_cut_fraction = c.fraction

        P_try = 1000 * (T_i ** (1.0 / 3.0) / watson_factor)

        if sub_fraction is not None and len(sub_fraction) > idx:
            F_i = sub_fraction[idx]

        yield (P_try, F_i, T_i)


def get_sa_mass_fractions(oil_obj):
    for P_try, F_i, T_i in get_ptry_values(oil_obj, K_sat):
        if T_i < 530.0:
            sg = P_try / 1000
            mw = None
            for v in oil_obj.molecular_weights:
                if np.isclose(v.ref_temp_k, T_i):
                    mw = v.saturate
                    break

            if mw is not None:
                f_sat = F_i * (2.2843 - 1.98138 * sg - 0.009108 * mw)

                if f_sat >= F_i:
                    f_sat = F_i
                elif f_sat < 0:
                    f_sat = 0

                f_arom = F_i * (1 - f_sat)

                yield (f_sat, f_arom)
            else:
                print '\tNo molecular weight at that temperature.'
        else:
            f_sat = f_arom = F_i / 2

            yield (f_sat, f_arom)


print 'oil cuts:'
pp.pprint(oil_obj.cuts)
print 'oil resins:', oil_obj.imported.resins
print 'oil aspaltenes:', oil_obj.imported.asphaltene_content
print 'oil imported cuts =', oil_obj.imported.cuts

print '\ninitial trial densities:'
K_arom = 10.0
K_sat = 12.0
ptry_values = (list(get_ptry_values(oil_obj, K_arom)) +
               list(get_ptry_values(oil_obj, K_sat)))

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

print '\naverage density based on trials using adjusted fractions:'
sa_ratios = list(get_sa_mass_fractions(oil_obj))
ptry_values = (list(get_ptry_values(oil_obj, K_sat,
                                    [r[0] for r in sa_ratios])) +
               list(get_ptry_values(oil_obj, K_arom,
                                    [r[1] for r in sa_ratios])))

print 'adjusted ptry_values:'
pp.pprint(ptry_values)
print sum([(P_try * F_i)
           for P_try, F_i, T_i in ptry_values] +
          [(1100.0 * f.fraction) for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')]
          )

print '\nSum of fractions:', sum([F_i for P_try, F_i, T_i in ptry_values])
print 'Oil sara fractions:', sum([f.fraction for f in oil_obj.sara_fractions
                                  if f.sara_type in ('Resins', 'Asphaltenes')])

print '\noil densities'
print oil_obj.densities












