"""Module contains functionality associated with grade profiles."""

import numpy as np
from math import radians, degrees, cos, sin, asin, atan2, sqrt


def get_grade(elev_ft_arr, coordinates=None, distances=None):
    # TODO: make units in %/100

    # check that n > 1
    if len(elev_ft_arr) < 2:
        raise ValueError(
            'Determining grade requires at least 2 coordinates\n\t\ti.e. Input size of n > 1')

    # if neither distance or coordinates are provided raise an exception
    if coordinates is None and distances is None:
        raise Exception('''
	Either distance or coordinates must be provided to the get_grade() function.
	''')

    # if only coordinates are provided, calculate the distance array
    if coordinates is not None and distances is None:
        distances = get_distances(coordinates)

    d_dist = distances  # distances is an iterable of distances in feet
    d_elev = np.diff(elev_ft_arr)
    grade = d_elev / d_dist
    grade = np.insert(grade, 0, 0)
    grade = np.round(grade, decimals=4)
    for a in range(len(grade) - 1):
        if np.isinf(grade[a + 1]) or np.isnan(grade[a + 1]):
            grade[a + 1] = grade[a]

    return d_dist, grade


def get_distances(coordinates):
    FT_PER_KM = 3280.84
    # place a zero up front
    distances = []
    i = 1
    while i < len(coordinates):
        lat1 = coordinates[i - 1][0]
        lon1 = coordinates[i - 1][1]
        lat2 = coordinates[i][0]
        lon2 = coordinates[i][1]
        dist_ft = haversine(lat1, lon1, lat2, lon2) * FT_PER_KM
        distances += [dist_ft]
        i += 1

    return distances


def haversine(lat1, lon1, lat2, lon2, get_bearing=False):
    """ 
    Calculates the great circle distance and bearing (if requested)
    between two points on the earth's surface

    args: lat1, lon1, lat2, lon2
        The arguments are latitude and longitude (in degree decimal format)
	coordinates

    kwargs: get_bearing
        False by default, when set to True, haversine returns bearing as well

    returns: distance in kilometers, bearing (if requested)
    """
    # convert decimal to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # compute haversine result
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    R = 6371  # radius of earth in km
    distance = c * R
    # round to centimeter precision
    distance = round(distance, 5)

    # compute bearing if requested
    if get_bearing:
        atan_arg1 = sin(dlon) * cos(lat2)
        atan_arg2 = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
        bearing = degrees(atan2(atan_arg1, atan_arg2))
        bearing = (bearing + 360) % 360
        # round to hundredth of degree precision
        bearing = round(bearing, 2)

        return distance, bearing

    else:
        return distance
