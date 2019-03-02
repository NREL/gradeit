"""Module contains functionality associated with elevation profiles."""

import requests
from json import loads

def get_elevation(coordinates):
    """
    A function that provides elevation values given coordinates

    Parameters:
        nested lists/tuples that contain latitude and longitude floating-point
        coordinates.

        ex:
            Tuple of tuples of floats
            ((xx.xxxxxx, xxx.xxxxxx), (xx.xxxxxx, xxx.xxxxxx))

            or

            List of lists of floats
            [[lat_1, lon_1], [lat_2, lon_2]]

    Returns:
        A tuple containing floating-point elevation values.

        ex:
            Tuple of floats
            (xxxx.xx, elev_2, elev_3, ...)
    """
    # TODO: make units in feet

    elevations = []

    # get each elevation value from USGS API
    for coord in coordinates:

        # query USGS API and store resulting elevation
        elev = usgs_api_elevation(coord)
        # append elevation to the elevations list
        elevations += [elev]

    return tuple(elevations)


def usgs_api_elevation(coordinate):
    """
    A function that queries the USGS DEM API (https://nationalmap.gov/epqs/) and
    returns the elevation value at the provided latitude/longitude coordinate.

    Parameters:
        List/Tuple that contains latitude and longitude floating-point
        values. These two values comprise a coordinate

        ex:
            Tuple of floats
            (xx.xxxxxx, xxx.xxxxxx)

            or

            List of floats
            [lat_1, lon_1]

    Returns:
        A float containing a floating-point elevation value.
    """
    # TODO: handle invalid elevation values (-1000000)

    URL = 'https://nationalmap.gov/epqs/pqs.php'
    lat = str(coordinate[0])
    lon = str(coordinate[1])
    UNITS = 'feet'
    OUTPUT = 'json'

    query = '{url}?x={lon}&y={lat}&units={units}&output={output}'.format(
            url=URL, lon=lon, lat=lat, units=UNITS, output=OUTPUT
            )

    response_json = requests.get(query)

    results = loads(response_json.text) # a dict containing the json data


    elev = results['USGS_Elevation_Point_Query_Service']\
                    ['Elevation_Query']\
                    ['Elevation']

    # cast value to a float
    elev = float(elev)

    return elev
