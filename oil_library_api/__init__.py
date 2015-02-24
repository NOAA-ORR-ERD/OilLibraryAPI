"""Main entry point
"""
import logging
logging.basicConfig()

from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.include("cornice")
    config.include('pyramid_mako')
    config.scan("oil_library_api.views")
    return config.make_wsgi_app()
