'''
    This is where we handle the initialization of the estimated oil properties.

    Basically, we have an Estimated object that is a one-to-one relationship
    with the Oil object.  This is where we will place the estimated oil
    properties.
'''
import transaction

from oil_library.models import Oil, Estimated


def process_estimates(session):
    print '\nPurging Categories...'
    for o in session.query(Oil):
        print 'Estimations for {0}'.format(o.adios_oil_id)
        o.estimated = Estimated()

    transaction.commit()