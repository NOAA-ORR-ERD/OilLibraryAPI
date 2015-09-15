"""Main entry point
"""
import logging
logging.basicConfig()

from pyramid.config import Configurator
from oil_library_api.common.views import cors_policy

def load_cors_origins(settings, key):
    if key in settings:
        origins = settings[key].split('\n')
        cors_policy['origins'] = origins

def main(global_config, **settings):

    load_cors_origins(settings, 'cors_policy.origins')

    config = Configurator(settings=settings)

    config.include("cornice")
    config.include('pyramid_mako')
    config.scan("oil_library_api.views")
    return config.make_wsgi_app()

