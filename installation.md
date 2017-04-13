# Installing the OilLibraryAPI server

**NOTE:** These instructions assume you are familiar with python package installation, and a littel bit with git / gitHub


## OilLIbrary Package

The OilLibraryAPI web server piggybacks on top of the existing oil_library
package that is related to the PyGnome project, and it depends on a
successful installation of that package.

Please go to the OilLibrary project and install it as a prerequisite for this
project:

https://github.com/NOAA-ORR-ERD/OilLibrary

### Get the code

(this is for the version on gitHub -- if you have another repo to access, use that url)

```
> git clone https://github.com/NOAA-ORR-ERD/OilLibrary.git
> cd OilLibrary
```
### Install the requirements

You can get the required packages from conda or (perhaps) pip. For more info about using conda, see the doc in the PyGNOME repo:

https://github.com/NOAA-ORR-ERD/PyGnome/blob/master/InstallingWithAnaconda.rst

```
> conda install --file requirements.txt
or
> pip install -r requirements.txt

### Installing the package

```
> python setup.py install
```

or

```
> python setup.py develop
```

Using "develop" mode will allow you to update the code without re-installing.

### testing

At this time, you should have the oil_library module available to you::

```
> python
> import oil_library  # the module should be available
```

and to test:

```
py.test
```

## Starting the Web API Server:

If the previous module imported correctly, you should be able to start the
OilLibrary web server.

### Getting the code and requirements

```
> git clone https://github.com/NOAA-ORR-ERD/OilLibraryAPI.git
> cd oillibraryapi
> conda install --file requirements.txt
```

or

```
> pip install -r requirements.txt
```

### installing the server package

> python setup.py install

### starting the server

```
> pserve config-example.ini
```

or

```
> pserve config-example.ini --reload
```

Using "--reload" allows the server to re-load itself when you change the code -- great for development, not required for running it.