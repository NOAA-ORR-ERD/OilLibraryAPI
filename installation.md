# Installing the OilLibraryAPI server

**NOTE:** These instructions assume you are familiar with python pacakge installation, etc.


The OilLibraryAPI web server piggybacks on top of the existing oil_library
package that is related to the PyGnome project, and it depends on a
successful installation of that package.

Please go to the OilLirary project and install it as a prerequisite of this
project:

https://github.com/NOAA-ORR-ERD/OilLibrary

This should work:

(this is for the version on gitHub -- if you have another repo to access, use that url)

```
> git clone https://github.com/NOAA-ORR-ERD/OilLibrary.git
> cd OilLibrary
> conda install --file requirements.txt
or
> pip install -r requirements.txt
> python setup.py install
```

At this time, you should have the oil_library module available to you::

```
> python
> import oil_library  # the module should be available
```

If the previous module imported correctly, you should be able to start the
OilLibrary web server.

```
> git clone https://github.com/NOAA-ORR-ERD/OilLibraryAPI.git
> cd oillibraryapi
> conda install --file requirements.txt
or
> pip install -r requirements.txt
> python setup.py install
> pserve development.ini --reload
```
