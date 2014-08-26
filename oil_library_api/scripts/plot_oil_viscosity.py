#!/usr/bin/env python

import sys
import os
import transaction

import numpy
np = numpy

import scipy
sp = scipy

import matplotlib
mpl = matplotlib
from matplotlib import pyplot
plt = pyplot

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from pyramid.paster import (get_appsettings,
                            setup_logging)

from pyramid.scripts.common import parse_vars

from oil_library.models import (DBSession,
                                Base,
                                Oil)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <adios oil id>\n'
          '(example: "%s development.ini  AD00047")' % (cmd, cmd))
    sys.exit(1)


def initialize_sql(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


def plot_oil_viscosities(settings):
    with transaction.manager:
        # -- Our loading routine --
        session = DBSession()

        if not 'adios_id' in settings:
            raise ValueError('adios_id setting is required.')
        adios_id = settings['adios_id']

        print 'our session: %s' % (session)
        try:
            oilobj = (session.query(Oil)
                      .filter(Oil.adios_oil_id == adios_id)
                      .one())
        except NoResultFound:
            raise NoResultFound('No Oil was found matching adios_id {0}'
                                .format(adios_id))

        if oilobj:
            print 'Our oil object: %s' % (oilobj)
            print 'Our unweathered viscosities (kg/m^3, Kdegrees):'
            vis = [v for v in oilobj.viscosities if v.weathering <= 0.0]
            for i in [(v.meters_squared_per_sec, v.ref_temp, v.weathering)
                      for v in vis]:
                print i
            x = np.array([v.ref_temp for v in vis]) - 273.15
            y = np.array([v.meters_squared_per_sec for v in vis])
            xmin = x.min()
            xmax = x.max()
            xpadding = .5 if xmax == xmin else (xmax - xmin) * .3
            ymin = y.min()
            ymax = y.max()
            ypadding = (ymax / 2) if ymax == ymin else (ymax - ymin) * .3
            plt.plot(x, y, 'ro')
            plt.xlabel(r'Temperature ($^\circ$C)')
            plt.ylabel('Unweathered Dynamic Viscosity (kg/m$^3$)')
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

                plt.annotate('(%s$^\circ$C, %s kg/m$^3$)' % (xx, yy),
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
        initialize_sql(settings)
        proc(settings)
    except:
        print "{0} FAILED\n".format(proc)
        raise
