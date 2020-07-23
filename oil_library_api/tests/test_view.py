"""
Functional tests for the view -- which is trivial
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class RootViewTests(FunctionalTestBase):
    def test_get_root_view(self):
        resp = self.testapp.get('/')
        result = resp.json_body
        assert result['Hello'] == "World, welcome to the Oil Library API!!"



