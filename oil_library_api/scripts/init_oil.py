'''
    This is where we handle the initialization of the estimated oil properties.
    This will be the 'real' oil record that we use.

    Basically, we have an Estimated object that is a one-to-one relationship
    with the Oil object.  This is where we will place the estimated oil
    properties.
'''
import transaction

from oil_library.models import ImportedRecord, Oil


def process_oils(session):
    print '\nPurging Categories...'
    for o in session.query(ImportedRecord):
        print 'Estimations for {0}'.format(o.adios_oil_id)
        o.oil = Oil()

    transaction.commit()
