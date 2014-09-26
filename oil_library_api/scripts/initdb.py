import os
import sys

import transaction
from sqlalchemy import engine_from_config

from pyramid.paster import (get_appsettings,
                            setup_logging)
from pyramid.scripts.common import parse_vars

from oil_library.oil_library_parse import OilLibraryFile

from oil_library.models import DBSession, Base

from .init_imported_record import purge_old_records, add_oil_object
from .init_categories import process_categories
from .init_oil import process_oils


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {0} <config_uri> [var=value]\n'
          '(example: "{0} development.ini")'.format(cmd))
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
        sys.stderr.write('Purging old Oil records in database')
        num_purged = purge_old_records(session)
        print 'finished!!!  {0} rows processed.'.format(num_purged)

        # 2. we need to open our OilLib file
        print 'opening file: {0} ...'.format(settings['oillib.file'])
        fd = OilLibraryFile(settings['oillib.file'])
        print 'file version:', fd.__version__

        # 3. iterate over our rows
        sys.stderr.write('Adding new Oil records to database')
        rowcount = 0
        for r in fd.readlines():
            if len(r) < 10:
                print 'got record:', r

            # 3a. for each row, we populate the Oil object
            add_oil_object(session, fd.file_columns, r)

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print 'finished!!!  {0} rows processed.'.format(rowcount)

        process_oils(session)
        process_categories(session)


def main(argv=sys.argv, proc=load_database):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri,
                               name='oil_library_api',
                               options=options)

    try:
        initialize_sql(settings)
        proc(settings)
    except:
        print "{0} FAILED\n".format(proc)
        raise
