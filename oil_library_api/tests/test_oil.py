"""
Functional tests for the Model Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from base import FunctionalTestBase


class OilTests(FunctionalTestBase):
    def test_get_oil_no_id(self):
        resp = self.testapp.get('/oil')
        oils = resp.json_body

        for r in oils:
            for k in ('adios_oil_id',
                      'api',
                      'categories',
                      'field_name',
                      'location',
                      'name',
                      'oil_class',
                      'pour_point',
                      'product_type',
                      'viscosity'):
                assert k in r

    def test_get_oil_invalid_id(self):
        self.testapp.get('/oil/{}'.format('bogus'), status=404)

    def test_get_oil_valid_id(self):
        resp = self.testapp.get('/oil/{0}'.format('AD00025'))
        oil = resp.json_body

        # the oil_library module has its own tests for all the oil
        # attributes, but we need to test that we conform to it.
        for k in ('adhesion',
                  'adios_oil_id',
                  'api',
                  'aromatics',
                  'asphaltene_content',
                  'benezene',
                  'categories',
                  'comments',
                  'conrandson_crude',
                  'conrandson_residuum',
                  'custom',
                  'cut_units',
                  'dispersability_temp_k',
                  'emuls_constant_max',
                  'emuls_constant_min',
                  'field_name',
                  'flash_point_max_k',
                  'flash_point_min_indicator',
                  'flash_point_min_k',
                  'k0y',
                  'location',
                  'naphthenes',
                  'nickel',
                  'oil_class',
                  'oil_name',
                  'oil_seawater_interfacial_tension_n_m',
                  'oil_seawater_interfacial_tension_ref_temp_k',
                  'oil_water_interfacial_tension_n_m',
                  'oil_water_interfacial_tension_ref_temp_k',
                  'paraffins',
                  'polars',
                  'pour_point_max_k',
                  'pour_point_min_indicator',
                  'pour_point_min_k',
                  'preferred_oils',
                  'product_type',
                  'reference',
                  'reid_vapor_pressure',
                  'resins',
                  'saturates',
                  'sulphur',
                  'vanadium',
                  'viscosity_multiplier',
                  'water_content_emulsion',
                  'wax_content'):
            assert k in oil

        for c in oil['cuts']:
            for k in ('fraction',
                      'liquid_temp_k',
                      'vapor_temp_k'):
                assert k in c

        for d in oil['densities']:
            for k in ('kg_m_3',
                      'ref_temp_k',
                      'weathering'):
                assert k in d

        for d in oil['dvis']:
            for k in ('kg_ms',
                      'ref_temp_k',
                      'weathering'):
                assert k in d

        for kvis in oil['kvis']:
            for k in ('m_2_s',
                      'ref_temp_k',
                      'weathering'):
                assert k in kvis

        for s in oil['synonyms']:
            for k in ('name',):
                assert k in s

        for t in oil['toxicities']:
            for k in (u'after_24_hours',
                      u'after_48_hours',
                      u'after_96_hours',
                      u'species',
                      u'tox_type'):
                assert k in t
