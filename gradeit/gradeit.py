"""Module contains the primary functionality of GradeIT."""

import elevation
import grade

def gradeit(coordinates):
    """
    A function that provides elevation and road grade values given coordinates

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
        A dictionary containing string keys and tuple values
        where the keys are 'elevation' and 'grade' and the values contain
        floating-point elevation and grade values.

        ex:
            grade_dictionary = {
                            'elevation' : (elev_val_1, elev_val_..., elev_val_n)
                            'grade' : (grade_val_1, grade_val_..., grade_val_n)
                            }
    """
    # get elevation values
    elev_tuple = elevation.get_elevation(coordinates)
    # get grade values
    grade_tuple = grade.get_grade(coordinates)

    # place both tuples in a dictionary
    gradeit_dict = {
                    'elevation':elev_tuple,
                    'grade':grade_tuple
                    }

    return gradeit_dict
