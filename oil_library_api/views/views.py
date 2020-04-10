""" Cornice services.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from cornice import Service


hello = Service(name='hello', path='/', description="Simplest app")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': 'World, welcome to the Oil Library API!!'}
