"""
Functional tests for the distinct call
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class RootViewTests(FunctionalTestBase):
    def test_get_root_view(self):
        resp = self.testapp.get('/gnome_oil/AD00009')
        result = resp.json_body
        print(result)

        assert result['name'] == 'ABU SAFAH'
        assert result['api'] == 28.0



