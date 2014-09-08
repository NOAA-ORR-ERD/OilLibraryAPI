"""Main entry point
"""
import logging
logging.basicConfig()

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    config = Configurator(settings=settings)

    config.include("cornice")
    config.include('pyramid_mako')
    config.scan("oil_library_api.views")
    return config.make_wsgi_app()
