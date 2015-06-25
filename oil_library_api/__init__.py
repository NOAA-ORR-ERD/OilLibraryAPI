"""Main entry point
"""
import logging
logging.basicConfig()

import ujson
from pyramid.config import Configurator
from pyramid.renderers import JSON as JSONRenderer


def get_json(request):
    return ujson.loads(request.text)


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)

    config.include("cornice")
    config.include('pyramid_mako')
    config.scan("oil_library_api.views")
    return config.make_wsgi_app()
