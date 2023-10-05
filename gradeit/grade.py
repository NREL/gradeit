from math import asin, cos, radians, sin, sqrt
from typing import List

import numpy as np

from gradeit.coordinate import Coordinate


def get_grade(elevation_profile: List[float], distances: List[float]) -> List[float]:
    # check that n > 1
    if len(elevation_profile) < 2:
        raise ValueError(
            "Determining grade requires at least 2 coordinates\n\t\ti.e. Input size of n > 1"
        )

    d_elev = np.diff(elevation_profile)
    grade = d_elev / distances
    grade = np.insert(grade, 0, 0)
    grade = np.round(grade, decimals=4)
    for a in range(len(grade) - 1):
        if np.isinf(grade[a + 1]) or np.isnan(grade[a + 1]):
            grade[a + 1] = grade[a]

    return list(grade)


def get_distances(coordinates: List[Coordinate]) -> List[float]:
    """
    Compute the distance between each coordinate pair
    """
    FT_PER_KM = 3280.84
    # place a zero up front
    distances = []
    i = 1
    while i < len(coordinates):
        dist_ft = haversine(coordinates[i - 1], coordinates[i]) * FT_PER_KM
        distances += [dist_ft]
        i += 1

    return distances


def haversine(coord1: Coordinate, coord2: Coordinate, get_bearing: bool = False) -> float:
    """
    Calculates the great circle distance and bearing (if requested)
    between two points on the earth's surface

    Parameters:
        coord1: a Coordinate object
        coord2: a Coordinate object

    Returns:
        distance: the great circle distance in km

    """
    # convert decimal to radians
    lat1 = radians(coord1.latitude)
    lon1 = radians(coord1.longitude)
    lat2 = radians(coord2.latitude)
    lon2 = radians(coord2.longitude)

    # compute haversine result
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    R = 6371  # radius of earth in km
    distance = c * R
    # round to centimeter precision
    distance = round(distance, 5)

    return distance
