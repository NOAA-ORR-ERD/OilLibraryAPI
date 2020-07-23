"""
base.py: Base classes for different types of tests.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os

from unittest import TestCase
from webtest import TestApp

from oil_library_api import main


class GnomeTestCase(TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.dirname(here))

    def get_settings(self):

        settings = {'cors_policy.origins': ('http://0.0.0.0:8080\n'
                                            'http://localhost:8080'),
                    'pyramid.default_locale_name': 'en',
                    'pyramid.includes': ('pyramid_tm\n'
                                         'cornice'),
                    'pyramid.debug_notfound': 'false',
                    'pyramid.debug_routematch': 'false',
                    'pyramid.debug_authorization': 'false',
                    'pyramid.reload_templates': 'true',
                    }

        return settings


class FunctionalTestBase(GnomeTestCase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()

        self.settings = self.get_settings()
        app = main(None, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        'Clean up any data the model generated after running tests.'
        pass
