#!/usr/bin/env python
import sys
import transaction

import numpy as np

try:
    import xlwt
    xlwt_available = True
except:
    print 'The xlwt module is not available!'
    xlwt_available = False

from oil_library import _get_db_session
from oil_library.models import ImportedRecord

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


def score_imported_oils(settings):
    '''
       Here is where we score the quality of the oil records that we have
       imported from the flatfile.
    '''
    adios_id = settings['adios_id'] if 'adios_id' in settings else None

    with transaction.manager:
        session = _get_db_session()

        if adios_id is not None:
            sys.stderr.write('scoring the imported oil record {0}...\n'
                             .format(adios_id))
            try:
                oil_obj = (session.query(ImportedRecord)
                           .filter(ImportedRecord.adios_oil_id == adios_id)
                           .one())

                to_xls = settings['to_xls'] if 'to_xls' in settings else None

                if to_xls is not None and xlwt_available:
                    export_oil_score_to_xls(oil_obj)
                else:
                    print '{0}\t{1}\t{2}'.format(oil_obj.adios_oil_id,
                                                 oil_obj.oil_name,
                                                 score_imported_oil(oil_obj))
            except:
                print 'Could not find record {0}'.format(adios_id)
                raise
        else:
            sys.stderr.write('scoring the imported oil records in database...')
            for o in session.query(ImportedRecord):
                print '{0}\t{1}\t{2}'.format(o.adios_oil_id,
                                             o.oil_name,
                                             score_imported_oil(o))


def score_imported_oil(imported_rec):
    scores = []
    scores.append(score_demographics(imported_rec))
    scores.append(score_api(imported_rec))
    scores.append(score_pour_point(imported_rec))
    scores.append(score_flash_point(imported_rec))
    scores.append(score_sara_fractions(imported_rec))
    scores.append(score_emulsion_constants(imported_rec))
    scores.append(score_interfacial_tensions(imported_rec))
    scores.append(score_densities(imported_rec))
    scores.append(score_viscosities(imported_rec))
    scores.append(score_cuts(imported_rec))
    scores.append(score_toxicities(imported_rec))

    return sum(scores) / len(scores)


def score_demographics(imported_rec):
    fields = ('oil_name', 'adios_oil_id',
              'location', 'field_name', 'reference', 'comments',
              'product_type', 'oil_class')
    scores = []

    for f in fields:
        if getattr(imported_rec, f) is not None:
            scores.append(1.0)
        else:
            scores.append(0.0)

    return sum(scores) / len(scores)


def score_api(imported_rec):
    scores = []

    if imported_rec.api is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_pour_point(imported_rec):
    scores = []

    if imported_rec.pour_point_min_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.pour_point_max_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_flash_point(imported_rec):
    scores = []

    if imported_rec.flash_point_min_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.flash_point_max_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_sara_fractions(imported_rec):
    scores = []

    if imported_rec.saturates is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.aromatics is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.asphaltene_content is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.resins is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_emulsion_constants(imported_rec):
    scores = []

    if imported_rec.emuls_constant_min is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.emuls_constant_max is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_interfacial_tensions(imported_rec):
    scores = []

    if imported_rec.oil_water_interfacial_tension_n_m is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.oil_water_interfacial_tension_ref_temp_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.oil_seawater_interfacial_tension_n_m is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    if imported_rec.oil_seawater_interfacial_tension_ref_temp_k is not None:
        scores.append(1.0)
    else:
        scores.append(0.0)

    return sum(scores) / len(scores)


def score_densities(imported_rec):
    scores = []

    for d in imported_rec.densities:
        # For right now, we will just check that the value at temperature
        # is there.  The weathering attribute is kinda optional
        if (d.kg_m_3 is not None and
                d.ref_temp_k is not None):
            scores.append(1.0)

    # We have a maximum number of 4 density field sets in our flat file
    # We can set a lower acceptable number later
    return sum(scores) / 4


def score_viscosities(imported_rec):
    scores = []

    scores.append(score_kvis(imported_rec))
    scores.append(score_dvis(imported_rec))

    return sum(scores) / len(scores)


def score_kvis(imported_rec):
    scores = []

    for k in imported_rec.kvis:
        # For right now, we will just check that the value at temperature
        # is there.  The weathering attribute is kinda optional
        if (k.m_2_s is not None and
                k.ref_temp_k is not None):
            scores.append(1.0)

    # We have a maximum number of 6 kvis field sets in our flat file
    # We can set a lower acceptable number later
    return sum(scores) / 6


def score_dvis(imported_rec):
    scores = []

    for d in imported_rec.dvis:
        # For right now, we will just check that the value at temperature
        # is there.  The weathering attribute is kinda optional.
        if (d.kg_ms is not None and
                d.ref_temp_k is not None):
            scores.append(1.0)

    # We have a maximum number of 6 dvis field sets in our flat file.
    # We can set a lower acceptable number later.
    return sum(scores) / 6


def score_cuts(imported_rec):
    scores = []

    for c in imported_rec.cuts:
        if (c.vapor_temp_k is not None and
                c.fraction is not None and
                c.fraction > 0.0 and
                c.fraction < 1.0):
            scores.append(1.0)

    # We have a maximum number of 15 cut field sets in our flat file.
    # We can set a lower acceptable number later.
    return sum(scores) / 15


def score_toxicities(imported_rec):
    scores = []

    for t in imported_rec.toxicities:
        if (t.species is not None and
                t.after_24h is not None and
                t.after_48h is not None and
                t.after_96h is not None):
            scores.append(1.0)

    # We have a maximum number of 3 EC toxicities and 3 LC toxicities
    # in our flat file.  We can set a lower acceptable number later.
    return sum(scores) / 6


def export_oil_score_to_xls(imported_rec):
    book = xlwt.Workbook(encoding="utf-8")

    add_oil_record_to_sheet(book.add_sheet("Oil Record"), imported_rec)

    add_densities_to_sheet(book.add_sheet("Densities"), imported_rec)

    add_viscosities_to_sheet(book.add_sheet("Viscosities"), imported_rec)

    add_cuts_to_sheet(book.add_sheet("Cuts"), imported_rec)

    add_toxicities_to_sheet(book.add_sheet("Toxicities"), imported_rec)

    add_scores_to_sheet(book.add_sheet("Scores"), imported_rec)

    book.save("{0}.xls".format(imported_rec.adios_oil_id))


def add_oil_record_to_sheet(sheet, imported_rec):
    fields = ('oil_name',
              'adios_oil_id',
              'custom',
              'location',
              'field_name',
              'reference',
              'api',
              'pour_point_min_k',
              'pour_point_max_k',
              'product_type',
              'comments',
              'asphaltene_content',
              'wax_content',
              'aromatics',
              'water_content_emulsion',
              'emuls_constant_min',
              'emuls_constant_max',
              'flash_point_min_k',
              'flash_point_max_k',
              'oil_water_interfacial_tension_n_m',
              'oil_water_interfacial_tension_ref_temp_k',
              'oil_seawater_interfacial_tension_n_m',
              'oil_seawater_interfacial_tension_ref_temp_k',
              'cut_units',
              'oil_class',
              'adhesion',
              'benezene',
              'naphthenes',
              'paraffins',
              'polars',
              'resins',
              'saturates',
              'sulphur',
              'reid_vapor_pressure',
              'viscosity_multiplier',
              'nickel',
              'vanadium',
              'conrandson_residuum',
              'conrandson_crude',
              'dispersability_temp_k',
              'preferred_oils',
              'k0y',)

    for idx, f in enumerate(fields):
        sheet.write(idx, 0, f)
        sheet.write(idx, 1, getattr(imported_rec, f),
                    xlwt.easyxf('align: horiz left'))

        col = sheet.col(0)
        col.width = 220 * 43
        col = sheet.col(1)
        col.width = 220 * 50


def add_densities_to_sheet(sheet, imported_rec):
    sheet.write(0, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(0, 1, 'kg/m^3', xlwt.easyxf('font: underline on;'))
    sheet.write(0, 2, 'Reference Temperature',
                xlwt.easyxf('font: underline on;'))
    sheet.write(0, 3, 'Weathering', xlwt.easyxf('font: underline on;'))
    col = sheet.col(2)
    col.width = 220 * 21

    for idx, d in enumerate(imported_rec.densities):
        sheet.write(1 + idx, 0, idx)
        sheet.write(1 + idx, 1, d.kg_m_3)
        sheet.write(1 + idx, 2, d.ref_temp_k)
        sheet.write(1 + idx, 3, d.weathering)


def add_viscosities_to_sheet(sheet, imported_rec):
    sheet.write_merge(0, 0, 0, 1, 'Kinematic Viscosities')
    sheet.write(1, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 1, 'm^2/s', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 2, 'Reference Temperature',
                xlwt.easyxf('font: underline on;'))
    sheet.write(1, 3, 'Weathering', xlwt.easyxf('font: underline on;'))
    col = sheet.col(2)
    col.width = 220 * 21

    idx = 0
    for idx, k in enumerate(imported_rec.kvis):
        sheet.write(2 + idx, 0, idx)
        sheet.write(2 + idx, 1, k.m_2_s)
        sheet.write(2 + idx, 2, k.ref_temp_k)
        sheet.write(2 + idx, 3, k.weathering)

    v_offset = 2 + idx + 2
    sheet.write_merge(v_offset, v_offset, 0, 1, 'Dynamic Viscosities')
    v_offset += 1
    sheet.write(v_offset, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 1, 'kg/ms', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 2, 'Reference Temperature',
                xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 3, 'Weathering', xlwt.easyxf('font: underline on;'))

    v_offset += 1
    for idx, d in enumerate(imported_rec.dvis):
        sheet.write(v_offset + idx, 0, idx)
        sheet.write(v_offset + idx, 1, d.kg_ms)
        sheet.write(v_offset + idx, 2, d.ref_temp_k)
        sheet.write(v_offset + idx, 3, d.weathering)


def add_cuts_to_sheet(sheet, imported_rec):
    sheet.write(0, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(0, 1, 'Vapor Temperature', xlwt.easyxf('font: underline on;'))
    sheet.write(0, 2, 'Liquid Temperature', xlwt.easyxf('font: underline on;'))
    sheet.write(0, 3, 'Fraction', xlwt.easyxf('font: underline on;'))
    col = sheet.col(1)
    col.width = 220 * 21
    col = sheet.col(2)
    col.width = 220 * 21

    for idx, c in enumerate(imported_rec.cuts):
        sheet.write(1 + idx, 0, idx)
        sheet.write(1 + idx, 1, c.vapor_temp_k)
        sheet.write(1 + idx, 2, c.liquid_temp_k)
        sheet.write(1 + idx, 3, c.fraction)


def add_toxicities_to_sheet(sheet, imported_rec):
    sheet.write_merge(0, 0, 0, 1, 'Effective Concentrations')
    sheet.write(1, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 1, 'Species', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 2, 'After 24H', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 3, 'After 48H', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 4, 'After 96H', xlwt.easyxf('font: underline on;'))

    idx = 0
    for idx, ec in enumerate([t for t in imported_rec.toxicities
                              if t.tox_type == 'EC']):
        sheet.write(2 + idx, 0, idx)
        sheet.write(2 + idx, 1, ec.species)
        sheet.write(2 + idx, 2, ec.after_24h)
        sheet.write(2 + idx, 3, ec.after_48h)
        sheet.write(2 + idx, 4, ec.after_96h)

    v_offset = 2 + idx + 2
    sheet.write_merge(v_offset, v_offset, 0, 1, 'Lethal Concentrations')
    v_offset += 1
    sheet.write(v_offset, 0, 'Index', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 1, 'Species', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 2, 'After 24H', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 3, 'After 48H', xlwt.easyxf('font: underline on;'))
    sheet.write(v_offset, 4, 'After 96H', xlwt.easyxf('font: underline on;'))

    v_offset += 1
    for idx, lc in enumerate([t for t in imported_rec.toxicities
                              if t.tox_type == 'LC']):
        sheet.write(v_offset + idx, 0, idx)
        sheet.write(v_offset + idx, 1, lc.species)
        sheet.write(v_offset + idx, 2, lc.after_24h)
        sheet.write(v_offset + idx, 3, lc.after_48h)
        sheet.write(v_offset + idx, 4, lc.after_96h)


def add_scores_to_sheet(sheet, imported_rec):
    sheet.write_merge(0, 0, 0, 1, 'Oil Category Scores')
    sheet.write(1, 0, 'Category', xlwt.easyxf('font: underline on;'))
    sheet.write(1, 1, 'Score', xlwt.easyxf('font: underline on;'))
    col = sheet.col(0)
    col.width = 220 * 27

    tests = (score_demographics,
             score_api,
             score_pour_point,
             score_flash_point,
             score_sara_fractions,
             score_emulsion_constants,
             score_interfacial_tensions,
             score_densities,
             score_viscosities,
             score_cuts,
             score_toxicities)

    idx = 0
    for idx, t in enumerate(tests):
        sheet.write(2 + idx, 0, t.__name__)
        sheet.write(2 + idx, 1, t(imported_rec))

    v_offset = 2 + idx + 2
    sheet.write(v_offset, 0, 'Overall Score')
    sheet.write(v_offset, 1,
                xlwt.Formula('AVERAGE($B$3:$B${0})'.format(v_offset)))
