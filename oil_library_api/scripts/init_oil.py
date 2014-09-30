'''
    This is where we handle the initialization of the estimated oil properties.
    This will be the 'real' oil record that we use.

    Basically, we have an Estimated object that is a one-to-one relationship
    with the Oil object.  This is where we will place the estimated oil
    properties.
'''
import transaction

from oil_library.models import ImportedRecord, Oil, KVis, Density


def process_oils(session):
    print '\nAdding Oil objects...'
    for rec in session.query(ImportedRecord):
        add_oil(rec)

    transaction.commit()


def add_oil(record):
    print 'Estimations for {0}'.format(record.adios_oil_id)
    oil = Oil()
    add_densities(record, oil)
    add_viscosities(record, oil)
    record.oil = oil


def add_densities(imported_rec, oil):
    '''
        Rules:
        - If no density value exists, estimate it from the API.
          So at the end, we will always have at least one density at
          15 degrees Celsius.
        - If a density measurement at some temperature exists, but no API,
          then we estimate API from density.
          So at the end, we will always have an API value.
        - In both the previous cases, we have estimated the corollary values
          and ensured that they are consistent.  But if a record contains both
          an API and a number of densities, these values may conflict.
          In this case, we will reject the creation of the oil record.
        - TODO: This is not in the document, but Bill & Chris have verbally
          stated they would like there to always be a 15C density value.
    '''
    if len(imported_rec.densities) == 0 and imported_rec.api is not None:
        # estimate our density from api
        print 'estimate density from api'
        kg_m_3, ref_temp_k = estimate_density_from_api(imported_rec.api)

        oil.densities.append(Density(kg_m_3=kg_m_3,
                                     ref_temp_k=ref_temp_k,
                                     weathering=0.0))
        oil.api = imported_rec.api
    elif imported_rec.api is None:
        # estimate our api from density
        print 'estimate our api from density'
        d_0 = density_at_temperature(imported_rec, 273.15 + 15)

        oil.api = (141.5 * 1000 / d_0) - 131.5
        for d in imported_rec.densities:
            oil.densities.append(d)
    else:
        # For now we will just accept both the api and densities
        # TODO: check if these values conflict
        print 'getting both values from imported record...'
        oil.api = imported_rec.api

        for d in imported_rec.densities:
            oil.densities.append(d)
        pass


def estimate_density_from_api(api):
    kg_m_3 = 141.5 / (131.5 + api) * 1000
    ref_temp_k = 273.15 + 15

    return kg_m_3, ref_temp_k


def density_at_temperature(oil_rec, temperature):
    # first, get the density record closest to our temperature
    density_rec = sorted([(d, abs(d.ref_temp_k - temperature))
                          for d in oil_rec.densities],
                         key=lambda d: d[1])[0][0]
    d_ref = density_rec.kg_m_3
    t_ref = density_rec.ref_temp_k
    k_pt = 0.008

    return d_ref / (1 - k_pt * (t_ref - temperature))


def add_viscosities(imported_rec, oil):
        '''
            Get a list of all kinematic viscosities associated with this
            oil object.  The list is compiled from the stored kinematic
            and dynamic viscosities associated with the oil record.
            The viscosity fields contain:
              - kinematic viscosity in m^2/sec
              - reference temperature in degrees kelvin
              - weathering ???
            Viscosity entries are ordered by (weathering, temperature)
            If we are using dynamic viscosities, we calculate the
            kinematic viscosity from the density that is closest
            to the respective reference temperature
        '''
        kvis = get_kvis(imported_rec)

        for kv, t, w in get_kvis_from_dvis(imported_rec):
            if kvis_exists_at_temp_and_weathering(kvis, t, w):
                continue

            kvis.append((kv, t, w))

        kvis.sort(key=lambda x: (x[2], x[1]))
        kwargs = ['m_2_s', 'ref_temp_k', 'weathering']

        for v in kvis:
            oil.kvis.append(KVis(**dict(zip(kwargs, v))))


def get_kvis(oil_rec):
    if oil_rec.kvis is not None:
        viscosities = [(k.m_2_s,
                        k.ref_temp_k,
                        (0.0 if k.weathering is None else k.weathering))
                       for k in oil_rec.kvis
                       if k.ref_temp_k is not None]
    else:
        viscosities = []

    return viscosities


def get_kvis_from_dvis(oil_rec):
    '''
        If we have any DVis records, we convert them to kinematic and return
        them.
        DVis records are correlated with a ref_temperature, and weathering.
        In order to convert dynamic viscosity to kinematic, we need to get
        the closest associated density
        - density must be at the same weathering
        - We use the density with a reference temperature closest to the DVis
          reference temperature.
    '''
    kvis_out = []

    if oil_rec.dvis:
        densities = [(d.kg_m_3,
                      d.ref_temp_k,
                      (0.0 if d.weathering is None else d.weathering))
                     for d in oil_rec.densities]

        for v, t, w in [(d.kg_ms,
                         d.ref_temp_k,
                         (0.0 if d.weathering is None else d.weathering))
                        for d in oil_rec.dvis]:
            matches_weathering = [(d[0], abs(t - d[1]))
                                  for d in densities
                                  if d[2] == w]

            if len(matches_weathering) == 0:
                continue

            # grab the density with the closest temperature
            # TODO: The density is close to our temperature, but not exact.
            #       We need to correct it for temperature.
            density = sorted(matches_weathering, key=lambda x: x[1])[0][0]

            # kvis = dvis/density
            kvis_out.append(((v / density), t, w))

    return kvis_out


def kvis_exists_at_temp_and_weathering(kvis, temperature, weathering):
    return len([v for v in kvis
                if v[1] == temperature
                and v[2] == weathering]) > 0
