#!/usr/bin/env python
import sys
import transaction

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import numpy
np = numpy

from oil_library.models import (DBSession,
                                ImportedRecord)


def score_imported_oils(settings):
    '''
       Here is where we score the quality of the oil records that we have
       imported from the flatfile.
    '''
    with transaction.manager:
        session = DBSession()

        sys.stderr.write('scoring the imported oil records in database...')
        for o in session.query(ImportedRecord):
            print o.adios_oil_id, o,
            print '\t\tScore: ', score_imported_oil(o)


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





