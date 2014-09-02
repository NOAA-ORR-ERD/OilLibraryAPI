'''
    This is where we handle the initialization of the oil categories.

    Basically, we have a number of oil categories arranged in a tree
    structure.  This will make it possible to create an expandable and
    collapsible way for users to find oils by the general 'type' of oil
    they are looking for, starting from very general types and navigating
    to more specific types.

    So we would like each oil to be linked to one or more of these
    categories.  For most of the oils we should be able to do this using
    generalized methods.  But there will very likely be some records
    we just have to link in a hard-coded way.

    The selection criteria for assigning refined products to different
    categories on the oil selection screen, depends upon the API (density)
    and the viscosity at a given temperature, usually at 38 C(100F).
    The criteria follows closely, but not identically, to the ASTM standards
'''
import transaction

from oil_library.models import Oil, Category
from oil_library.oil_props import OilProps

def clear_categories(session):
    categories = session.query(Category).filter(Category.parent == None)

    rowcount = 0
    for o in categories:
        session.delete(o)
        rowcount += 1

    transaction.commit()
    return rowcount


def load_categories(session):
    crude = Category('Crude')
    refined = Category('Refined')
    other = Category('Other')

    crude.append('Condensate')
    crude.append('Light')
    crude.append('Medium')
    crude.append('Heavy')

    refined.append('Light Products (Fuel Oil 1)')
    refined.append('Gasoline')
    refined.append('Kerosene')

    refined.append('Fuel Oil 2')
    refined.append('Diesel')
    refined.append('Heating Oil')

    refined.append('Intermediate Fuel Oil')

    refined.append('Fuel Oil 6 (HFO)')
    refined.append('Bunker')
    refined.append('Heavy Fuel Oil')
    refined.append('Group 5')

    other.append('Vegetable Oils/Biodiesel')
    other.append('Dilbit')
    other.append('Bitumen')

    session.add_all([crude, refined, other])
    transaction.commit()


def list_categories(category, indent=0):
    '''
        This is a recursive method to print out our categories
        showing the nesting with tabbed indentation.
    '''
    yield '{0}{1}'.format(' ' * indent, category.name)
    for c in category.children:
        for y in list_categories(c, indent + 4):
            yield y


def link_oils_to_categories(session):
    # now we try to link the oil records with our categories
    # in some kind of automated fashion
    link_crude_light_oils(session)
    link_crude_medium_oils(session)
    link_crude_heavy_oils(session)

    link_refined_fuel_oil_1(session)
    link_refined_fuel_oil_2(session)
    link_refined_ifo(session)
    link_refined_fuel_oil_6(session)

    show_uncategorized_oils(session)


def link_crude_light_oils(session):
    # our category
    top_category = (session.query(Category)
                    .filter(Category.name == 'Crude').one())
    category = [c for c in top_category.children if c.name == 'Light'][0]

    # our oils
    oils = (session.query(Oil)
            .filter(Oil.api > 31.1)
            .filter(Oil.product_type == 'Crude')
            .all())

    count = 0
    for o in oils:
        o.categories.append(category)
        count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name, category.name))
    transaction.commit()


def link_crude_medium_oils(session):
    # our category
    top_category = (session.query(Category)
                    .filter(Category.name == 'Crude').one())
    category = [c for c in top_category.children if c.name == 'Medium'][0]

    # our oils
    oils = (session.query(Oil)
            .filter(Oil.api <= 31.1)
            .filter(Oil.api > 22.3)
            .filter(Oil.product_type == 'Crude')
            .all())

    count = 0
    for o in oils:
        o.categories.append(category)
        count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name, category.name))
    transaction.commit()


def link_crude_heavy_oils(session):
    # our category
    top_category = (session.query(Category)
                    .filter(Category.name == 'Crude').one())
    category = [c for c in top_category.children if c.name == 'Heavy'][0]

    # our oils
    oils = (session.query(Oil)
            .filter(Oil.api <= 22.3)
            .filter(Oil.product_type == 'Crude')
            .all())

    count = 0
    for o in oils:
        o.categories.append(category)
        count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name, category.name))
    transaction.commit()


def link_refined_fuel_oil_1(session):
    '''
       Category Name:
       - Fuel oil #1/gasoline/kerosene
       Sample Oils:
       - gasoline
       - kerosene
       - JP-4
       - avgas
       Density Criteria:
       - API >= 35
       Kinematic Viscosity Criteria:
       - v <= 2.5 cSt @ 38 degrees Celcius
    '''
    top_category = (session.query(Category)
                    .filter(Category.name == 'Refined').one())
    categories = [c for c in top_category.children
                  if c.name in ('Light Products (Fuel Oil 1)',
                                'Gasoline',
                                'Kerosene')
                  ]

    oils = (session.query(Oil)
            .filter(Oil.api >= 35.0)
            .filter(Oil.product_type == 'Refined')
            .all())

    count = 0
    category_temp = 273.15 + 38
    for o in oils:
        oil_props = OilProps(o, temperature=category_temp)
        if oil_props.get_viscosity('cSt') <= 2.5:
            for category in categories:
                o.categories.append(category)
            count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name,
                   [n.name for n in categories]))
    transaction.commit()


def link_refined_fuel_oil_2(session):
    '''
       Category Name:
       - Fuel oil #2/Diesel/Heating Oil
       Sample Oils:
       - Diesel
       - Heating Oil
       - No. 2 Distillate
       Density Criteria:
       - 30 <= API < 35
       Kinematic Viscosity Criteria:
       - 2.5 < v <= 4.0 cSt @ 38 degrees Celcius
    '''
    top_category = (session.query(Category)
                    .filter(Category.name == 'Refined').one())
    categories = [c for c in top_category.children
                  if c.name in ('Fuel Oil 2',
                                'Diesel',
                                'Heating Oil')
                  ]

    oils = (session.query(Oil)
            .filter(Oil.api >= 30.0)
            .filter(Oil.api < 35.0)
            .filter(Oil.product_type == 'Refined')
            .all())

    count = 0
    category_temp = 273.15 + 38
    for o in oils:
        oil_props = OilProps(o, temperature=category_temp)
        visc = oil_props.get_viscosity('cSt')
        if visc > 2.5 or visc <= 4.0:
            for category in categories:
                o.categories.append(category)
            count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name,
                   [n.name for n in categories]))
    transaction.commit()


def link_refined_ifo(session):
    '''
       Category Name:
       - Intermediate Fuel Oil
       Sample Oils:
       - IFO 180
       - Fuel Oil #4
       - Marine Diesel
       Density Criteria:
       - 15 <= API < 30
       Kinematic Viscosity Criteria:
       - 4.0 < v < 200.0 cSt @ 38 degrees Celcius
    '''
    top_category = (session.query(Category)
                    .filter(Category.name == 'Refined').one())
    categories = [c for c in top_category.children
                  if c.name in ('Intermediate Fuel Oil',)
                  ]

    oils = (session.query(Oil)
            .filter(Oil.api >= 15.0)
            .filter(Oil.api < 30.0)
            .filter(Oil.product_type == 'Refined')
            .all())

    count = 0
    category_temp = 273.15 + 38
    for o in oils:
        oil_props = OilProps(o, temperature=category_temp)
        visc = oil_props.get_viscosity('cSt')
        if visc > 4.0 or visc < 200.0:
            for category in categories:
                o.categories.append(category)
            count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name,
                   [n.name for n in categories]))
    transaction.commit()


def link_refined_fuel_oil_6(session):
    '''
       Category Name:
       - Fuel Oil #6/Bunker/Heavy Fuel Oil/Group 5
       Sample Oils:
       - Bunker C
       - Residual Oil
       Density Criteria:
       - API < 15
       Kinematic Viscosity Criteria:
       - 200.0 <= v cSt @ 50 degrees Celcius
    '''
    top_category = (session.query(Category)
                    .filter(Category.name == 'Refined').one())
    categories = [c for c in top_category.children
                  if c.name in ('Fuel Oil 6',
                                'Bunker',
                                'Heavy Fuel Oil',
                                'Group 5')
                  ]

    oils = (session.query(Oil)
            .filter(Oil.api >= 0.0)
            .filter(Oil.api < 15.0)
            .filter(Oil.product_type == 'Refined')
            .all())

    count = 0
    category_temp = 273.15 + 50
    for o in oils:
        oil_props = OilProps(o, temperature=category_temp)
        visc = oil_props.get_viscosity('cSt')
        if visc >= 200.0:
            for category in categories:
                o.categories.append(category)
            count += 1

    print ('{0} oils added to {1} -> {2}.'
           .format(count, top_category.name,
                   [n.name for n in categories]))
    transaction.commit()


def show_uncategorized_oils(session):
    oils = (session.query(Oil)
            .filter(Oil.categories == None)
            .all())

    print ('{0} oils uncategorized.'
           .format(len(oils)))
