
from sqlalchemy import engine_from_config
from sqlalchemy.orm.relationships import (RelationshipProperty,
                                          ONETOMANY)

from pyramid.paster import (get_appsettings,
                            setup_logging)

from oil_library_api.models import DBSession
from oil_library.models import Base, Oil, Toxicity

session = DBSession()

oil = session.query(Oil).filter(Oil.name == 'AUTOMOTIVE GASOLINE, EXXON')[0]
oil.tojson()

cut = oil.cuts[0]
cut.tojson()

for o in session.query(Oil):
    if o.toxicities:
        print
        print [t.species for t in o.toxicities]
        print [t.after_24_hours for t in o.toxicities]
        print [t.after_48_hours for t in o.toxicities]
        print [t.after_96_hours for t in o.toxicities]

