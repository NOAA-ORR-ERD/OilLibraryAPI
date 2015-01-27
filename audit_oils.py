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
from oil_library.init_oil import density_at_temperature

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


def get_ptry_values(oil_obj, component_type, sub_fraction=None):
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
    watson_factors = {'Saturates': 12, 'Aromatics': 10}
    watson_factor = watson_factors[component_type]

    previous_cut_fraction = 0.0
    for idx, c in enumerate(oil_obj.cuts):
        T_i = c.vapor_temp_k

        F_i = c.fraction - previous_cut_fraction
        previous_cut_fraction = c.fraction

        P_try = 1000 * (T_i ** (1.0 / 3.0) / watson_factor)

        if sub_fraction is not None and len(sub_fraction) > idx:
            F_i = sub_fraction[idx]

        yield (P_try, F_i, T_i, component_type)


def get_sa_mass_fractions(oil_obj):
    for P_try, F_i, T_i, c_type in get_ptry_values(oil_obj, 'Saturates'):
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
print 'oil imported cuts =', oil_obj.imported.cuts

print '\ninitial trial densities:'
K_arom = 10.0
K_sat = 12.0
ptry_values = (list(get_ptry_values(oil_obj, 'Aromatics')) +
               list(get_ptry_values(oil_obj, 'Saturates')))

for r in ptry_values:
    print '\t', r

for f in oil_obj.sara_fractions:
    if f.sara_type in ('Resins', 'Asphaltenes'):
        print '\t', (1100.0, f.fraction)

print '\naverage density based on trials assuming equal sub-fractions:'
print sum([(P_try * (F_i * 0.5))
           for P_try, F_i, T_i, c_type in ptry_values] +
          [(1100.0 * f.fraction) for f in oil_obj.sara_fractions
           if f.sara_type in ('Resins', 'Asphaltenes')]
          )

print '\nNow try to get saturate/aromatic mass fractions based on trials'
print 'molecular weights:'
for mw in oil_obj.molecular_weights:
    print '\t', (mw.saturate, mw.aromatic, mw.ref_temp_k)

print '\naverage density based on trials using adjusted fractions:'
sa_ratios = list(get_sa_mass_fractions(oil_obj))
ptry_values = (list(get_ptry_values(oil_obj, 'Saturates',
                                    [r[0] for r in sa_ratios])) +
               list(get_ptry_values(oil_obj, 'Aromatics',
                                    [r[1] for r in sa_ratios])))

ra_ptry_values = [(1100.0, f.fraction)
                  for f in oil_obj.sara_fractions
                  if f.sara_type in ('Resins', 'Asphaltenes')]

print 'adjusted ptry_values:'
pp.pprint(ptry_values)
print 'average ptry', (sum([(P_try * F_i)
                            for P_try, F_i, T_i, c_type in ptry_values]) /
                       sum([(F_i) for P_try, F_i, T_i, c_type in ptry_values]))

ptry_avg_density = sum([(P_try * F_i)
                        for P_try, F_i, T_i, c_type in ptry_values] +
                       [(P_try * F_i)
                        for P_try, F_i in ra_ptry_values]
                       )

total_sa_fraction = sum([F_i for P_try, F_i, T_i, c_type in ptry_values])
print '\nSum of SA fractions:', total_sa_fraction

total_ra_fraction = sum([f.fraction for f in oil_obj.sara_fractions
                         if f.sara_type in ('Resins', 'Asphaltenes')])
print 'Sum of RA fractions:', total_ra_fraction
print 'Sum of SARA fractions:', total_sa_fraction + total_ra_fraction

# our estimated RA fractions deviate a bit from the imported RA fractions
print 'oil resins:', oil_obj.imported.resins
print 'oil aspaltenes:', oil_obj.imported.asphaltene_content

print '\nAdjusted avg density:', ptry_avg_density

oil_density = density_at_temperature(oil_obj, 288.15)
print 'Oil density at 288K:', oil_density

print ('percent deviation: {0}'
       .format((oil_density - ptry_avg_density) / oil_density * 100))

print '\n\nNow we will try to adjust our ptry densities to match the oil total density'
oil_sa_avg_density = ((oil_density - total_ra_fraction * 1100.0) /
                      total_sa_fraction)
print 'SA avg density approximated from Oil & SARA fractions:', oil_sa_avg_density

density_adjustment = oil_sa_avg_density / ptry_avg_density
print 'adjusting ptry densities by a factor of', density_adjustment

ptry_values = [(P_try * density_adjustment, F_i, T_i)
               for P_try, F_i, T_i, c_type in ptry_values]

print 'Density adjusted ptry_values:'
pp.pprint(ptry_values)
ptry_avg_density = sum([(P_try * F_i) for P_try, F_i, T_i in ptry_values] +
                       [(1100.0 * f.fraction)
                        for f in oil_obj.sara_fractions
                        if f.sara_type in ('Resins', 'Asphaltenes')])
print '\nDensity adjusted avg density:', ptry_avg_density

print ('percent deviation: {0}'
       .format((oil_density - ptry_avg_density) / oil_density * 100))


for o in session.query(Oil):
    if o.bullwinkle_fraction > 1.0:
        print 'Bullwinkle Fraction:', o.bullwinkle_fraction,
        print 'Asphaltene Fraction: ', [af for af in o.sara_fractions
                                        if af.sara_type == 'Asphaltenes'],
        print 'API:', o.api

for o in session.query(Oil):
    if o.bullwinkle_fraction < 0.0:
        print 'Bullwinkle Fraction:', o.bullwinkle_fraction,
        print 'Asphaltene Fraction: ', [af for af in o.sara_fractions
                                        if af.sara_type == 'Asphaltenes'],
        print 'API:', o.api





