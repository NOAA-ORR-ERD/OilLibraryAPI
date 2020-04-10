"""
Common Gnome object request handlers.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

cors_policy = {'credentials': True}

def obj_id_from_url(request):
    # the pyramid URL parser returns a tuple of 0 or more
    # matching items, at least when using the * wild card
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None


def obj_id_from_req_payload(json_request):
    return json_request.get('id')
