"""Module contains functionality associated with grade profiles."""

# NOTE: temporary for functon i/o testing
from numpy.random import randint

def get_grade(coordinates):
    """
    A function that provides road grade values given coordinates

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
        A tuple containing floating-point grade values.

        ex:
            Tuple of floats
            (xxxx.xx, elev_2, elev_3, ...)
    """
    # TODO: make units in %/100

    # check that n > 1
    if len(coordinates) < 2:
        raise ValueError('Determining grade requires at least 2 coordinates\n\t\ti.e. Input size of n > 1')

    grades = []

    # get each elevation value
    for coord in coordinates:

        # TODO: make this an actual grade value from the database
        grade = float(randint(100, 100000)) / 100
        # append it to the elevations list
        grades += [grade]

    return tuple(grades)
