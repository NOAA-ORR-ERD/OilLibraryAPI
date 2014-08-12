""" Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='oil_library_api',
      version=0.1,
      description='OilLibraryAPI',
      long_description=README,
      classifiers=["Programming Language :: Python",
                   "Framework :: Pylons",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
                   ],
      keywords="adios gnome oilspill weathering trajectory modeling",
      author='ADIOS/GNOME team at NOAA ORR',
      author_email='orr.gnome@noaa.gov',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['cornice', 'waitress', 'pyramid_mako'],
      entry_points=('[paste.app_factory]\n'
                    '  main = oil_library_api:main\n'
                    '[console_scripts]\n'
                    '  init_oil_library = oil_library_api.scripts.initdb:main\n'
                    '  audit_oil_library = oil_library_api.scripts.initdb:audit\n'
                    '  export_oil_library = oil_library_api.scripts.initdb:export\n'
                    ),
      paster_plugins=['pyramid'],
)
