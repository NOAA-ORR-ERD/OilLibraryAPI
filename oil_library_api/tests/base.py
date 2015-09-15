"""
base.py: Base classes for different types of tests.
"""
import os
import shutil
from unittest import TestCase

from paste.deploy.loadwsgi import appconfig
from webtest import TestApp

from oil_library_api import main


class GnomeTestCase(TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.dirname(here))

    def get_settings(self,
                     config_file='../../config-example.ini#oil_library_api'):
        here = os.path.dirname(__file__)
        return appconfig('config:%s' % config_file, relative_to=here)


class FunctionalTestBase(GnomeTestCase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()

        self.settings = self.get_settings()
        app = main(None, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        'Clean up any data the model generated after running tests.'
        pass
