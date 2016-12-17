#!/usr/bin/env python
import sys

import numpy as np
import transaction

try:
    import xlwt
    xlwt_available = True
except:
    print 'The xlwt module is not available!'
    xlwt_available = False

from oil_library import _get_db_session
from oil_library.models import ImportedRecord


def aggregate_score(Q_i, w_i=None):
    '''
        General method for aggregating a number of sub-scores.
        We implement a weighted average for this.
    '''
    Q_i = np.array(Q_i)

    if w_i is None:
        w_i = np.ones(Q_i.shape)
    else:
        w_i = np.array(w_i)

    return np.sum(w_i * Q_i) / np.sum(w_i)


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
                imp_obj = (session.query(ImportedRecord)
                           .filter(ImportedRecord.adios_oil_id == adios_id)
                           .one())
            except:
                print 'Could not find imported record {0}'.format(adios_id)
                raise

            to_xls = settings['to_xls'] if 'to_xls' in settings else None

            if to_xls is not None and xlwt_available:
                export_oil_score_to_xls(imp_obj)
            else:
                print '{0}\t{1}\t{2}'.format(imp_obj.adios_oil_id,
                                             imp_obj.oil_name,
                                             score_imported_oil(imp_obj))
        else:
            sys.stderr.write('scoring the imported oil records in database...')
            for o in session.query(ImportedRecord):
                print '{0}\t{1}\t{2}'.format(o.adios_oil_id,
                                             o.oil_name,
                                             score_imported_oil(o))


def score_imported_oil(imported_rec):
    scores = [(score_api(imported_rec), 5.0),
              (score_densities(imported_rec), 5.0),
              (score_viscosities(imported_rec), 5.0),
              (score_sara_fractions(imported_rec), 5.0),
              (score_cuts(imported_rec), 5.0),
              (score_pour_point(imported_rec), 5.0),
              (score_demographics(imported_rec), 1.0),
              (score_flash_point(imported_rec), 1.0),
              (score_interfacial_tensions(imported_rec), 1.0),
              (score_emulsion_constants(imported_rec), 1.0),
              (score_toxicities(imported_rec), 1.0)]

    return aggregate_score(*zip(*scores))


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

    return aggregate_score(scores)


def score_api(imported_rec):
    if imported_rec.api is None:
        return 0.0
    else:
        return 1.0


def score_densities(imported_rec):
    scores = []

    for d in imported_rec.densities:
        scores.append(score_density_rec(d))

    # We have a maximum number of 4 density field sets in our flat file
    # We can set a lower acceptable number later
    if len(scores) < 4:
        scores += [0.0] * (4 - len(scores))

    # compute our weights
    w_i = 1.0 / (2.0 ** (np.arange(len(scores)) + 1))
    w_i[-1] = w_i[-2]  # duplicate the last weight so we sum to 1.0

    return aggregate_score(scores, w_i)


def score_density_rec(density_rec):
    if (density_rec.kg_m_3 is not None and
            density_rec.ref_temp_k is not None):
        return 1.0
    else:
        return 0.0


def score_pour_point(imported_rec):
    scores = []

    scores.append(score_pour_point_max(imported_rec))
    scores.append(score_pour_point_min(imported_rec))
    w_i = [2.0, 1.0]

    return aggregate_score(scores, w_i)


def score_flash_point(imported_rec):
    if (imported_rec.flash_point_min_k is not None or
            imported_rec.flash_point_max_k is not None):
        return 1.0
    else:
        return 0.0


def score_pour_point_min(imported_rec):
    return (1.0 if imported_rec.pour_point_min_k is not None else 0.0)


def score_pour_point_max(imported_rec):
    return (1.0 if imported_rec.pour_point_max_k is not None else 0.0)


def score_sara_fractions(imported_rec):
    scores = []

    scores.append(score_sara_saturates(imported_rec))
    scores.append(score_sara_aromatics(imported_rec))
    scores.append(score_sara_resins(imported_rec))
    scores.append(score_sara_asphaltenes(imported_rec))

    return aggregate_score(scores)


def score_sara_saturates(imported_rec):
    return (1.0 if imported_rec.saturates is not None else 0.0)


def score_sara_aromatics(imported_rec):
    return (1.0 if imported_rec.aromatics is not None else 0.0)


def score_sara_resins(imported_rec):
    return (1.0 if imported_rec.resins is not None else 0.0)


def score_sara_asphaltenes(imported_rec):
    return (1.0 if imported_rec.asphaltenes is not None else 0.0)


def score_emulsion_constants(imported_rec):
    scores = []

    scores.append(score_emulsion_constant_min(imported_rec))
    scores.append(score_emulsion_constant_max(imported_rec))

    return aggregate_score(scores)


def score_emulsion_constant_min(imported_rec):
    return (1.0 if imported_rec.emuls_constant_min is not None else 0.0)


def score_emulsion_constant_max(imported_rec):
    return (1.0 if imported_rec.emuls_constant_max is not None else 0.0)


def score_interfacial_tensions(imported_rec):
    scores = []

    scores.append(score_oil_water_tension(imported_rec))
    scores.append(score_oil_seawater_tension(imported_rec))

    return aggregate_score(scores)


def score_oil_water_tension(imported_rec):
    rec = imported_rec
    if (rec.oil_water_interfacial_tension_n_m is not None and
            rec.oil_water_interfacial_tension_ref_temp_k is not None):
        return 1.0
    else:
        return 0.0


def score_oil_seawater_tension(imported_rec):
    rec = imported_rec
    if (rec.oil_seawater_interfacial_tension_n_m is not None and
            rec.oil_seawater_interfacial_tension_ref_temp_k is not None):
        return 1.0
    else:
        return 0.0


def score_viscosities(imported_rec):
    scores = []
    all_temps = set()
    all_viscosities = []

    for v in imported_rec.kvis + imported_rec.dvis:
        if v.ref_temp_k not in all_temps:
            all_viscosities.append(v)
            all_temps.add(v.ref_temp_k)

    for v in all_viscosities:
        scores.append(score_single_viscosity(v))

    # We require a minimum number of 4 viscosity field sets
    if len(scores) < 4:
        scores += [0.0] * (4 - len(scores))

    # compute our weights
    w_i = 1.0 / (2.0 ** (np.arange(len(scores)) + 1))
    w_i[-1] = w_i[-2]  # duplicate the last weight so we sum to 1.0

    return aggregate_score(scores, w_i)


def score_single_viscosity(viscosity_rec):
    temp = viscosity_rec.ref_temp_k

    try:
        value = viscosity_rec.m_2_s
    except AttributeError:
        value = viscosity_rec.kg_ms

    if (value is not None and temp is not None):
        return 1.0
    else:
        return 0.0


def score_cuts(imported_rec):
    scores = []

    for c in imported_rec.cuts:
        scores.append(score_single_cut(c))

    # We would like a minimum number of 10 distillation cuts
    if len(scores) < 10:
        scores += [0.0] * (10 - len(scores))

    return aggregate_score(scores)


def score_single_cut(cut_rec):
    scores = []

    scores.append(cut_has_vapor_temp(cut_rec))
    scores.append(cut_has_fraction(cut_rec))
    scores.append(cut_has_liquid_temp(cut_rec))

    if not all([(s == 1.0) for s in scores[:2]]):
        return 0.0
    else:
        w_i = [4.5, 4.5, 1.0]
        return aggregate_score(scores, w_i)


def cut_has_vapor_temp(cut_rec):
    return (0.0 if cut_rec.vapor_temp_k is None else 1.0)


def cut_has_liquid_temp(cut_rec):
    return (0.0 if cut_rec.liquid_temp_k is None else 1.0)


def cut_has_fraction(cut_rec):
    return (0.0 if cut_rec.fraction is None else 1.0)


def score_toxicities(imported_rec):
    scores = []

    for t in imported_rec.toxicities:
        scores.append(score_single_toxicity(t))

    if any([(s == 1.0) for s in scores]):
        return 1.0
    else:
        return 0.0


def score_single_toxicity(tox_rec):
    if (tox_rec.species is not None and
        (tox_rec.after_24h is not None or
         tox_rec.after_48h is not None or
         tox_rec.after_96h is not None)):
        return 1.0
    else:
        return 0.0


def export_oil_score_to_xls(imported_rec):
    book = xlwt.Workbook(encoding="utf-8")

    add_oil_record_to_sheet(book.add_sheet("Oil Record"), imported_rec)

    add_densities_to_sheet(book.add_sheet("Densities"), imported_rec)

    add_viscosities_to_sheet(book.add_sheet("Viscosities"), imported_rec)

    add_cuts_to_sheet(book.add_sheet("Cuts"), imported_rec)

    add_toxicities_to_sheet(book.add_sheet("Toxicities"), imported_rec)

    add_scores_to_sheet(book.add_sheet("Scores"), imported_rec)

    if imported_rec.oil is not None:
        add_sara_fractions_to_sheet(book.add_sheet("SARA Fractions"),
                                    imported_rec.oil)
        add_sara_densities_to_sheet(book.add_sheet("SARA Densities"),
                                    imported_rec.oil)
        add_molecular_weights_to_sheet(book.add_sheet("Molecular Weights"),
                                       imported_rec.oil)

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
              'asphaltenes',
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
              'benzene',
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
    col.width = 220 * 22

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
    col.width = 220 * 22

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


def add_sara_fractions_to_sheet(sheet, oil_rec):
    header_style = xlwt.easyxf('font: underline on;')
    sheet.write(0, 0, 'Index', header_style)
    sheet.write(0, 1, 'SARA Type', header_style)
    sheet.write(0, 2, 'Reference Temperature', header_style)
    sheet.write(0, 3, 'Fraction', header_style)

    col = sheet.col(2)
    col.width = 220 * 22

    for idx, c in enumerate(oil_rec.sara_fractions):
        sheet.write(1 + idx, 0, idx)
        sheet.write(1 + idx, 1, c.sara_type)
        sheet.write(1 + idx, 2, c.ref_temp_k)
        sheet.write(1 + idx, 3, c.fraction)


def add_sara_densities_to_sheet(sheet, oil_rec):
    header_style = xlwt.easyxf('font: underline on;')
    sheet.write(0, 0, 'Index', header_style)
    sheet.write(0, 1, 'SARA Type', header_style)
    sheet.write(0, 2, 'Reference Temperature', header_style)
    sheet.write(0, 3, 'Density (kg/m^3)', header_style)

    col = sheet.col(2)
    col.width = 220 * 22
    col = sheet.col(3)
    col.width = 220 * 16

    for idx, c in enumerate(oil_rec.sara_densities):
        sheet.write(1 + idx, 0, idx)
        sheet.write(1 + idx, 1, c.sara_type)
        sheet.write(1 + idx, 2, c.ref_temp_k)
        sheet.write(1 + idx, 3, c.density)


def add_molecular_weights_to_sheet(sheet, oil_rec):
    header_style = xlwt.easyxf('font: underline on;')
    sheet.write(0, 0, 'Index', header_style)
    sheet.write(0, 1, 'SARA Type', header_style)
    sheet.write(0, 2, 'Reference Temperature', header_style)
    sheet.write(0, 3, 'Molecular Weight (g/mol)', header_style)

    col = sheet.col(2)
    col.width = 220 * 22
    col = sheet.col(3)
    col.width = 220 * 23

    for idx, c in enumerate(oil_rec.molecular_weights):
        sheet.write(1 + idx, 0, idx)
        sheet.write(1 + idx, 1, c.sara_type)
        sheet.write(1 + idx, 2, c.ref_temp_k)
        sheet.write(1 + idx, 3, c.g_mol)
