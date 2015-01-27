#!/usr/bin/env python
import sys
import transaction

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import numpy
np = numpy

try:
    import xlwt
    xlwt_available = True
except:
    print 'The xlwt module is not available!'
    xlwt_available = False

from oil_library.models import (DBSession,
                                ImportedRecord)


def score_imported_oils(settings):
    '''
       Here is where we score the quality of the oil records that we have
       imported from the flatfile.
    '''
    adios_id = settings['adios_id'] if 'adios_id' in settings else None

    with transaction.manager:
        session = DBSession()

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

    sheet1 = book.add_sheet("Oil Record")
    add_oil_record_to_sheet(sheet1, imported_rec)

    # scores = []
    # scores.append(score_demographics(imported_rec))
    # scores.append(score_api(imported_rec))
    # scores.append(score_pour_point(imported_rec))
    # scores.append(score_flash_point(imported_rec))
    # scores.append(score_sara_fractions(imported_rec))
    # scores.append(score_emulsion_constants(imported_rec))
    # scores.append(score_interfacial_tensions(imported_rec))
    # scores.append(score_densities(imported_rec))
    # scores.append(score_viscosities(imported_rec))
    # scores.append(score_cuts(imported_rec))
    # scores.append(score_toxicities(imported_rec))

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
        col.width = 200 * 44
        col = sheet.col(1)
        col.width = 200 * 50







