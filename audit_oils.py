
from sqlalchemy import engine_from_config

from pyramid.paster import (get_appsettings,
                            setup_logging)

from oil_library.models import DBSession, Base, Oil, Toxicity

settings = app.registry.settings
engine = engine_from_config(settings, 'sqlalchemy.')
DBSession.configure(bind=engine)
session = DBSession()

for o in session.query(Oil):
    if o.toxicities:
        print
        print [t.species for t in o.toxicities]
        print [t.after_24_hours for t in o.toxicities]
        print [t.after_48_hours for t in o.toxicities]
        print [t.after_96_hours for t in o.toxicities]

