#!/usr/bin/env python

"""
some example code to access the oil_library API
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# third party libary, but really nice.
#  "conda install requests" or "pip install requests"
import requests

# this is the currently running server at NOAA
# (as of 1/11/2017 -- no guarantees as to what it will be in the future)

base_url = "http://161.55.65.31:443/"

# Load the main searchable list of the library:
oil_url = base_url + "oil"
print("fetching the entire oil list")
r = requests.get(oil_url)

# This returns a list of dicts -- one dict for each oil
all_oils = r.json()

print("There are %i oils in the Database" % len(all_oils))

print("Here are all the fields in one record:")
print("Note: these are only the fields that are there for searching, etc.")
for k in all_oils[37].keys():
    print(k)

# find one with "alaska" in the name:
alaska_oils = [(rec['name'], rec['adios_oil_id']) for rec in all_oils if "alaska" in rec['name'].lower()]

for oil in alaska_oils:
    print(oil)

# Now let's look at a full record:

# requesting the record for "ALASKA NORTH SLOPE (NORTHERN PIPELINE)"
#  adios_oil_id = AD01760
r = requests.get(oil_url + "/AD01760")
record = r.json()

#Lots of info there:
print("Here are all the fields in a complete record:")
for k in record.keys():
    print(k)

# for instance, here are the densities measured:
# two in this case
for density in record['densities']:
    print(density)





