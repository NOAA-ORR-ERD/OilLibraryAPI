# Installing the OilLibraryAPI server

The OilLibraryAPI web server piggybacks on top of the existing oil_library
module that is found inside the PyGnome project, and it depends on a
successful installation of that project.

Please go to the PyGnome project and install it as a prerequisite of this
project.

Of course, if you don't need the full capabilities of PyGnome, and would simply
like to use the oil_library, you can follow these slightly-simpler instructions::

```
> git checkout <url_to_py_gnome>
> cd <path_to_py_gnome>
> cd oil_library
> python setup.py develop
```

At this time, you should have the oil_library module available to you::

```
> python
> import oil_library  # the module should be available
```

If the previous module imported correctly, you should be able to start the
OilLibrary web server.

```
> git checkout <url_to_oil_library_api>
> cd <path_to_oil_library_api>
> pserve development.ini --reload
```
