from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (get_appsettings,
                            setup_logging)

from pyramid.scripts.common import parse_vars

from oil_library import _get_db_session
from oil_library.models import (Base,
                                ImportedRecord,
                                Oil)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {0} <config_uri> [var=value]\n'
          '(example: "{0} development.ini")'.format(cmd))
    sys.exit(1)


def initialize_sql(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


def audit_distillation_cuts(settings):
    '''
       Just a quick check of the data values that we loaded
       when we initialized the database.
    '''
    with transaction.manager:
        session = _get_db_session()

        sys.stderr.write('Auditing the records in database...')
        num_cuts = []
        liquid_temp = []
        vapor_temp = []
        fraction = []
        for o in session.query(Oil):
            num_cuts.append(len(o.cuts))
            for i, cut in enumerate(o.cuts):
                if len(liquid_temp) > i:
                    if cut.liquid_temp_k:
                        liquid_temp[i].append(cut.liquid_temp_k)
                    if cut.vapor_temp_k:
                        vapor_temp[i].append(cut.vapor_temp_k)
                    if cut.fraction:
                        fraction[i].append(cut.fraction)
                else:
                    liquid_temp.append([])
                    vapor_temp.append([])
                    fraction.append([])

        print ('\nNumber of cut entries (min, max, avg): ({0}, {1}, {2})'
               .format(min(num_cuts),
                       max(num_cuts),
                       float(sum(num_cuts)) / len(num_cuts))
               )

        print('\nLiquid Temperature:')
        for i in range(len(liquid_temp)):
            if len(liquid_temp[i]) > 0:
                temp = liquid_temp[i]
                avg = float(sum(temp)) / len(temp)
                print ('\tCut #{0} (set-size, min, max, avg): '
                       '({1}, {2}, {3}, {4})'
                       .format(i, len(temp), min(temp), max(temp), avg))
            else:
                temp = liquid_temp[i]
                print ('\tCut #{0} (set-size, min, max, avg): '
                       '({1}, {2}, {3}, {4})'
                       .format(i, len(temp), None, None, None))

        print('\nVapor Temperature:')
        for i in range(len(vapor_temp)):
            print ('\tCut #{0} (set-size, min, max, avg): '
                   '({1}, {2}, {3}, {4})'
                   .format(i,
                           len(vapor_temp[i]),
                           min(vapor_temp[i]),
                           max(vapor_temp[i]),
                           float(sum(vapor_temp[i])) / len(vapor_temp[i]))
                   )

        print('\nFraction:')
        for i in range(len(fraction)):
            print ('\tCut #{0} (set-size, min, max, avg): '
                   '({1}, {2}, {3}, {4})'
                   .format(i,
                           len(fraction[i]),
                           min(fraction[i]),
                           max(fraction[i]),
                           float(sum(fraction[i])) / len(fraction[i]))
                   )

        print('finished!!!')


def audit_database(settings):
    '''
       Just a quick check of the data values that we loaded
       when we initialized the database.
    '''
    with transaction.manager:
        session = _get_db_session()

        sys.stderr.write('Auditing the records in database...')
        for o in session.query(ImportedRecord):
            if 1 and o.synonyms:
                    print()
                    print([s.name for s in o.synonyms])

            if 1 and o.densities:
                    print()
                    print([d.kg_m_3 for d in o.densities])
                    print([d.ref_temp_k for d in o.densities])
                    print([d.weathering for d in o.densities])

            if 1 and o.kvis:
                    print()
                    print([k.m_2_s for k in o.kvis])
                    print([k.ref_temp_k for k in o.kvis])
                    print([k.weathering for k in o.kvis])

            if 1 and o.dvis:
                    print()
                    print([d.kg_ms for d in o.dvis])
                    print([d.ref_temp_k for d in o.dvis])
                    print([d.weathering for d in o.dvis])

            if 1 and o.cuts:
                    print()
                    print([c.vapor_temp_k for c in o.cuts])
                    print([c.liquid_temp_k for c in o.cuts])
                    print([c.fraction for c in o.cuts])

            if 1:
                tox = [t for t in o.toxicities if t.tox_type == 'EC']
                if tox:
                    print()
                    print([t.species for t in tox])
                    print([t.after_24h for t in tox])
                    print([t.after_48h for t in tox])
                    print([t.after_96h for t in tox])

            if 1:
                tox = [t for t in o.toxicities if t.tox_type == 'LC']
                if tox:
                    print()
                    print([t.species for t in tox])
                    print([t.after_24h for t in tox])
                    print([t.after_48h for t in tox])
                    print([t.after_96h for t in tox])

        print('finished!!!')


def export_database(settings):
    '''
       Just a quick check of the data values that we loaded
       when we initialized the database.
    '''
    with transaction.manager:
        session = _get_db_session()

        sys.stderr.write('Exporting the records in database...')
        for o in session.query(Oil):
            print(o)
            print(o.tojson())


def export(argv=sys.argv):
    main(argv, export_database)


def audit_cuts(argv=sys.argv):
    main(argv, audit_distillation_cuts)


def audit(argv=sys.argv):
    main(argv, audit_database)


def main(argv=sys.argv, proc=export_database):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri,
                               name='oil_library_api',
                               options=options)

    try:
        proc(settings)
    except:
        print("{0} FAILED\n".format(proc))
        raise
