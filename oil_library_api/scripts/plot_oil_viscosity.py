#!/usr/bin/env python

import sys
import os
import transaction

import numpy as np

from matplotlib import pyplot as plt

from sqlalchemy.orm.exc import NoResultFound

from pyramid.paster import (get_appsettings,
                            setup_logging)

from pyramid.scripts.common import parse_vars

from oil_library import _get_db_session
from oil_library.models import Oil, ImportedRecord
from oil_library.oil_props import OilProps


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {0} <config_uri> <adios oil id>\n'
          '(example: "{0} development.ini adios_id=AD00047")'.format(cmd))
    sys.exit(1)


def plot_oil_viscosities(settings):
    with transaction.manager:
        # -- Our loading routine --
        session = _get_db_session()

        if 'adios_id' not in settings:
            raise ValueError('adios_id setting is required.')
        adios_id = settings['adios_id']

        print 'our session: %s' % (session)
        try:
            oilobj = (session.query(Oil).join(ImportedRecord)
                      .filter(ImportedRecord.adios_oil_id == adios_id)
                      .one())
        except NoResultFound:
            raise NoResultFound('No Oil was found matching adios_id {0}'
                                .format(adios_id))

        if oilobj:
            print 'Our oil object: %s' % (oilobj)

            oil_props = OilProps(oilobj)
            print '\nOilProps:', oil_props
            print oil_props.kvis_at_temp()

            print '\nOur viscosities:'
            print [v for v in oilobj.kvis]

            print '\nOur unweathered viscosities (m^2/s, Kdegrees):'
            vis = [v for v in oilobj.kvis if v.weathering <= 0.0]
            print vis
            for i in [(v.m_2_s, v.ref_temp_k, v.weathering)
                      for v in vis]:
                print i

            x = np.array([v.ref_temp_k for v in vis]) - 273.15
            y = np.array([v.m_2_s for v in vis])
            xmin = x.min()
            xmax = x.max()
            xpadding = .5 if xmax == xmin else (xmax - xmin) * .3
            ymin = y.min()
            ymax = y.max()
            ypadding = (ymax / 2) if ymax == ymin else (ymax - ymin) * .3
            plt.plot(x, y, 'ro')
            plt.xlabel(r'Temperature ($^\circ$C)')
            plt.ylabel('Unweathered Kinematic Viscosity (m$^2$/s)')
            plt.yscale('log', subsy=[2, 3, 4, 5, 6, 7, 8, 9])
            plt.grid(True)
            plt.axis([xmin - xpadding, xmax + xpadding, 0, ymax + ypadding])

            # now we add the annotations
            for xx, yy in np.vstack((x, y)).transpose():
                print (xx, yy)
                if xx > x.mean():
                    xalign = -xpadding / 3
                else:
                    xalign = xpadding / 3
                yalign = ypadding / 3

                plt.annotate('(%s$^\circ$C, %s m$^2$/s)' % (xx, yy),
                             xy=(xx + (xalign / 10),
                                 yy + (yalign / 10)),
                             xytext=(xx + xalign, yy + yalign),
                             arrowprops=dict(facecolor='black',
                                             shrink=0.01),
                             fontsize=9)
            plt.show()


def main(argv=sys.argv, proc=plot_oil_viscosities):
    if len(argv) < 3:
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
        print "{0} FAILED\n".format(proc)
        raise
