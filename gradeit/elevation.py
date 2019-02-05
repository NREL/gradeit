"""Module contains functionality associated with elevation profiles."""

# NOTE: temporary for functon i/o testing
from numpy.random import randint

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

    # get each elevation value
    for coord in coordinates:

        # TODO: make this an actual elevation value from the database
        elev = float(randint(100, 100000)) / 100
        # append it to the elevations list
        elevations += [elev]

    return tuple(elevations)


