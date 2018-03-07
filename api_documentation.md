# API Documentation

This web server's API has been designed specifically to be used with the PyGnome web client
(the WebGnomeClient project)

As such, it is very simple and has no additional features beyond what the client needs.

So without further hesitation, Here are the APIs.

## /distinct

Example: `http://0.0.0.0:9898/distinct`

This link supplies a list of unique values for certain searchable fields that the web client needs to build its oil querying form.

It returns a JSON structure similar to the example below:

```javascript
[{"column": "location",
  "values": ["SAUDI ARABIA",
             "RAS TANURA,
             "SAUDI ARABIA",
             ...
             "KUPARUK",
             "CALGARY, ALBERTA"]},
 {"column": "field_name",
  "values": ["ABU SAFAH",
             "ALGERIAN BLEND",
             "ALGERIAN CONDENSATE",
             "ARABIAN EXTRA LIGHT",
             "ARABIAN HEAVY",
             ...
             "NORTHSTAR",
             "BACHAQUERO-DELAWARE RIVER",
             "CONDENSATE (SWEET)"]},
 {"column": "product_type",
  "values": {"Crude": ["Condensate",
                       "Light",
                       "Medium",
                       "Heavy"],
             "Refined": ["Light Products (Fuel Oil 1)",
                         "Gasoline",
                         "Kerosene",
                         "Fuel Oil 2",
                         "Diesel",
                         "Heating Oil",
                         "Intermediate Fuel Oil",
                         "Fuel Oil 6 (HFO)",
                         "Bunker",
                         "Heavy Fuel Oil",
                         "Group V"],
             "Other": ["Other"]
             }
  }
 ]
```

## /oil

Example: `http://0.0.0.0:9898/oil`


This link returns a JSON structure containing a list of searchable fields for all oils in the database.  Keep in mind that this is not every attribute of every oil, but just the fields that the web client can use to search for oils.

It returns a JSON structure similar to the example below:

```javascript
[{"pour_point": [244.0, 244.0],
  "api": 28.0,
  "product_type": "Crude",
  "name": "ABU SAFAH",
  "oil_class": "Group 3",
  "adios_oil_id": "AD00009",
  "field_name": "ABU SAFAH",
  "categories": ["Crude-Medium"],
  "viscosity": 0.0000142888,
  "location": "SAUDI ARABIA"},
 {"pour_point": [244.0, 244.0],
  "api": 45.5,
  "product_type": "Crude",
  "name": "ALGERIAN BLEND",
  "oil_class": "Group 1",
  "adios_oil_id": "AD00026",
  "field_name": "ALGERIAN BLEND",
  "categories": ["Crude-Light"],
  "viscosity": 0.0000059537,
  "location": "ALGERIA"},
 ...
 {"pour_point": [273.0, 273.0],
  "api": 11.8,
  "product_type": "Crude",
  "name": "BACHAQUERO-DELAWARE RIVER, CITGO",
  "oil_class": "Group 4",
  "adios_oil_id": "AD02482",
  "field_name": "BACHAQUERO-DELAWARE RIVER",
  "categories": ["Crude-Heavy"],
  "viscosity": 0.0022326287,
  "location": null}
 ]
```

## /oil/{adios_oil_id}

Example: `http://0.0.0.0:9898/oil/AD00009`


This link searches for an oil record based on the passed-in identifier, and returns a JSON structure containing all the attributes of that oil


It returns a JSON structure similar to the example below:

```javascript
{
 "name": "ABU SAFAH",
 "adios_oil_id": "AD00009",
 "api": 28.0,
 "pour_point_min_k": 244.0,
 "pour_point_max_k": 244.0,
 "flash_point_min_k": null,
 "flash_point_max_k": 363.48,
 "oil_water_interfacial_tension_n_m": 0.0318012,
 "oil_water_interfacial_tension_ref_temp_k": 288.15,
 "oil_seawater_interfacial_tension_n_m": null,
 "oil_seawater_interfacial_tension_ref_temp_k": null,
 "emulsion_water_fraction_max": 0.9,
 "sulphur_fraction": 0.0,
 "bullwinkle_fraction": 0.303,
 "bullwinkle_time": null,
 "adhesion_kg_m_2": 0.035,
 "soluability": 0.0,
 "k0y": 0.00000202,
 "molecular_weights": [{"sara_type": "Saturates",
                        "g_mol": 124.2651232685,
                        "ref_temp_k": 416.7529892363},
                       ...
                       {"sara_type": "Aromatics",
                        "g_mol": 693.6049027647,
                        "ref_temp_k": 842.7097031268}
                       ],
 "cuts": [{"vapor_temp_k": 416.7529892363,
           "liquid_temp_k": null,
           "fraction": 0.1767095188,
           "imported_record_id": null},
          ...
          {"vapor_temp_k": 842.7097031268,
           "liquid_temp_k": null,
           "fraction": 0.883547594,
           "imported_record_id": null}
          ],
 "estimated": {"emulsion_water_fraction_max": true,
               "name": false
               "pour_point_max_k": false,
               "densities": false,
               "oil_water_interfacial_tension_n_m": true,
               "oil_water_interfacial_tension_ref_temp_k": true,
               "sara_fractions": true,
               "soluability": true,
               "flash_point_min_k": true,
               "sulphur_fraction": true,
               "flash_point_max_k": true,
               "api": false,
               "molecular_weights": true,
               "viscosities": false,
               "cuts": true,
               "adhesion_kg_m_2": true,
               "pour_point_min_k": false,
               "bullwinkle_fraction": true,
               },
 "categories": [{"name": "Medium",
                 "parent": {"name": "Crude"},
                 "children": []}
                ],
 "sara_densities": [{"density": 1100.0,
                     "sara_type": "Asphaltenes",
                     "ref_temp_k": 1015.0},
                    ...
                    {"density": 965.3369871262,
                     "sara_type": "Aromatics",
                     "ref_temp_k": 842.7097031268}
                    ],
 "densities": [{"ref_temp_k": 288.15,
                "kg_m_3": 887.1473354232,
                "weathering": 0.0}
               ],
 "sara_fractions": [{"sara_type": "Resins",
                     "ref_temp_k": 1015.0,
                     "fraction": 0.0912699723},
                    {"sara_type": "Asphaltenes",
                     "ref_temp_k": 1015.0,
                     "fraction": 0.0251824337},
                    ...
                    {"sara_type": "Saturates",
                     "ref_temp_k": 416.7529892363,
                     "fraction": 0.0},
                    {"sara_type": "Aromatics",
                     "ref_temp_k": 416.7529892363,
                     "fraction": 0.1767095188},
                    ],
 "kvis": [{"m_2_s": 0.000025,
           "ref_temp_k": 294.0,
           "weathering": 0.0},
          ...
          {"m_2_s": 0.0000144,
           "ref_temp_k": 311.0,
           "weathering": 0.0}
          ]
 }
```

## Example usage of the API

Here is some example Python code that uses the API:

```
#!/usr/bin/env python

"""
some example code to access the oil_library API
"""

# third party libary, but really nice.
#  "conda install requests" or "pip install requests"
import requests

# this is the currently running server at NOAA
# (as of 3/07/2018 -- no guarantees as to what it will be in the future)
base_url = "https://oillibraryapi.orr.noaa.gov:80/"

# if running locally, it may be something like:
# base_url = "http://0.0.0.0:9898"


# Load the main searchable list of the library:
oil_url = base_url + "oil"
print "fetching the entire oil list"
r = requests.get(oil_url)

# This returns a list of dicts -- one dict for each oil
all_oils = r.json()

print "There are %i oils in the Database" % len(all_oils)

print "Here are all the fields in one record:"
print "Note: these are only the fields that are there for searching, etc."
for k in all_oils[37].keys():
    print k

# find one with "alaska" in the name:
alaska_oils = [(rec['name'], rec['adios_oil_id']) for rec in all_oils if "alaska" in rec['name'].lower()]

print "\n*********"
print 'All oils with "alaska" in the name:'
for oil in alaska_oils:
    print oil

# Now let's look at a full record:

# requesting the record for "ALASKA NORTH SLOPE (NORTHERN PIPELINE)"
#  adios_oil_id = AD01760
r = requests.get(oil_url + "/AD01760")
record = r.json()

#Lots of info there:
print "\n*********"
print "Here are all the fields in a complete record:"
for k in record.keys():
    print k

# for instance, here are the densities measured:
# two in this case
print "\n*********"
print "And here are the density fields:"
for density in record['densities']:
    print density

```
