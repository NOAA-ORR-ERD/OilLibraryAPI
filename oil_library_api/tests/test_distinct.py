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
        resp = self.testapp.get('/distinct')
        result = resp.json_body
        cols = [d["column"] for d in result]
        cols.sort()
        # not much, but it's something
        assert cols == ['field_name', 'location', 'product_type']



