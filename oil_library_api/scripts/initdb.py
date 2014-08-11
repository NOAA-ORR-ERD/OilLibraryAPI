import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (get_appsettings,
                            setup_logging)

from pyramid.scripts.common import parse_vars

from oil_library.oil_library_parse import OilLibraryFile

from oil_library.models import (DBSession,
                                Base,
                                Oil,
                                Synonym,
                                Density,
                                KVis,
                                DVis,
                                Cut,
                                Toxicity)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def initialize_sql(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


def load_database(settings):
    with transaction.manager:
        # -- Our loading routine --
        session = DBSession()

        # 1. purge our builtin rows if any exist
        sys.stderr.write('Purging old records in database')
        num_purged = purge_old_records(session)
        print 'finished!!!  %d rows processed.' % (num_purged)

        # 2. we need to open our OilLib file
        print 'opening file: %s ...' % (settings['oillib.file'])
        fd = OilLibraryFile(settings['oillib.file'])
        print 'file version:', fd.__version__

        # 3. iterate over our rows
        sys.stderr.write('Adding new records to database')
        rowcount = 0
        for r in fd.readlines():
            if len(r) < 10:
                print 'got record:', r

            # 3a. for each row, we populate the Oil object
            add_oil_object(session, fd.file_columns, r)

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print 'finished!!!  %d rows processed.' % (rowcount)


def purge_old_records(session):
    oilobjs = session.query(Oil).filter(Oil.custom == False)

    rowcount = 0
    for o in oilobjs:
        session.delete(o)

        if rowcount % 100 == 0:
            sys.stderr.write('.')

        rowcount += 1

    transaction.commit()
    return rowcount


def add_oil_object(session, file_columns, row_data):
    row_dict = dict(zip(file_columns, row_data))
    transaction.begin()
    oil = Oil(**row_dict)

    add_synonyms(session, oil, row_dict)
    add_densities(oil, row_dict)
    add_kinematic_viscosities(oil, row_dict)
    add_dynamic_viscosities(oil, row_dict)
    add_distillation_cuts(oil, row_dict)
    add_toxicity_effective_concentrations(oil, row_dict)
    add_toxicity_lethal_concentrations(oil, row_dict)

    session.add(oil)
    transaction.commit()


def add_synonyms(session, oil, row_dict):
    if row_dict.get('Synonyms'):
        for s in row_dict.get('Synonyms').split(','):
            s = s.strip()
            if len(s) > 0:
                synonyms = session.query(Synonym).filter(Synonym.name == s).all()
                if len(synonyms) > 0:
                    # we link the existing synonym object
                    oil.synonyms.append(synonyms[0])
                else:
                    # we add a new synonym object
                    oil.synonyms.append(Synonym(s))


def add_densities(oil, row_dict):
    for i in range(1, 5):
        obj_args = ('(kg/m^3)', 'Ref Temp (K)', 'Weathering')
        row_fields = ['Density#{0} {1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            densityargs = {}

            for col, arg in zip(row_fields, obj_args):
                densityargs[arg] = row_dict.get(col)

            oil.densities.append(Density(**densityargs))


def add_kinematic_viscosities(oil, row_dict):
    for i in range(1, 7):
        obj_args = ('(m^2/s)', 'Ref Temp (K)', 'Weathering')
        row_fields = ['KVis#{0} {1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            kvisargs = {}

            for col, arg in zip(row_fields, obj_args):
                kvisargs[arg] = row_dict.get(col)

            oil.kvis.append(KVis(**kvisargs))


def add_dynamic_viscosities(oil, row_dict):
    for i in range(1, 7):
        obj_args = ('(kg/ms)', 'Ref Temp (K)', 'Weathering')
        row_fields = ['DVis#{0} {1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            dvisargs = {}

            for col, arg in zip(row_fields, obj_args):
                dvisargs[arg] = row_dict.get(col)

            oil.dvis.append(DVis(**dvisargs))


def add_distillation_cuts(oil, row_dict):
    for i in range(1, 16):
        obj_args = ('Vapor Temp (K)', 'Liquid Temp (K)', 'Fraction')
        row_fields = ['Cut#{0} {1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            cutargs = {}

            for col, arg in zip(row_fields, obj_args):
                cutargs[arg] = row_dict.get(col)

            oil.cuts.append(Cut(**cutargs))


def add_toxicity_effective_concentrations(oil, row_dict):
    for i in range(1, 4):
        obj_args = ('Species', '24h', '48h', '96h')
        row_fields = ['Tox_EC({0}){1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            toxargs = {}
            toxargs['Toxicity Type'] = 'EC'

            for col, arg in zip(row_fields, obj_args):
                toxargs[arg] = row_dict.get(col)

            oil.toxicities.append(Toxicity(**toxargs))


def add_toxicity_lethal_concentrations(oil, row_dict):
    for i in range(1, 4):
        obj_args = ('Species', '24h', '48h', '96h')
        row_fields = ['Tox_LC({0}){1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            toxargs = {}
            toxargs['Toxicity Type'] = 'LC'

            for col, arg in zip(row_fields, obj_args):
                toxargs[arg] = row_dict.get(col)

            oil.toxicities.append(Toxicity(**toxargs))


def audit_database(settings):
    '''
       Just a quick check of the data values that we loaded
       when we initialized the database.
    '''
    with transaction.manager:
        session = DBSession()

        sys.stderr.write('Auditing the records in database')
        for o in session.query(Oil):
            if 1 and o.synonyms:
                    print
                    print [s.name for s in o.synonyms]

            if 1 and o.densities:
                    print
                    print [d.kg_per_m_cubed for d in o.densities]
                    print [d.ref_temp for d in o.densities]
                    print [d.weathering for d in o.densities]

            if 1 and o.kvis:
                    print
                    print [k.meters_squared_per_sec for k in o.kvis]
                    print [k.ref_temp for k in o.kvis]
                    print [k.weathering for k in o.kvis]

            if 1 and o.dvis:
                    print
                    print [d.kg_per_msec for d in o.dvis]
                    print [d.ref_temp for d in o.dvis]
                    print [d.weathering for d in o.dvis]

            if 1 and o.cuts:
                    print
                    print [c.vapor_temp for c in o.cuts]
                    print [c.liquid_temp for c in o.cuts]
                    print [c.fraction for c in o.cuts]

            if 1:
                tox = [t for t in o.toxicities if t.tox_type == 'EC']
                if tox:
                    print
                    print [t.species for t in tox]
                    print [t.after_24_hours for t in tox]
                    print [t.after_48_hours for t in tox]
                    print [t.after_96_hours for t in tox]

            if 1:
                tox = [t for t in o.toxicities if t.tox_type == 'LC']
                if tox:
                    print
                    print [t.species for t in tox]
                    print [t.after_24_hours for t in tox]
                    print [t.after_48_hours for t in tox]
                    print [t.after_96_hours for t in tox]

        print 'finished!!!'


def audit(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    try:
        initialize_sql(settings)
        audit_database(settings)
    except:
        print "FAILED TO AUDIT OIL LIBRARY DATABASE\n"
        raise


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    try:
        initialize_sql(settings)
        load_database(settings)
    except:
        print "FAILED TO CREATED OIL LIBRARY DATABASE \n"
        raise
