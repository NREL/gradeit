"""Module contains the primary functionality of GradeIT."""

import elevation
import grade

def gradeit(coordinates, source='usgs-api'):
    """
    A function that provides elevation and road grade values given coordinates

    Parameters:
	coordinates:
	    nested lists/tuples that contain latitude and longitude floating-point
            coordinates.

            ex: Tuple of tuples of floats
                ((xx.xxxxxx, xxx.xxxxxx), (xx.xxxxxx, xxx.xxxxxx))

                or

                List of lists of floats
                [[lat_1, lon_1], [lat_2, lon_2]]

	source:
	    valid keywords are:
		
		'usgs-api' (default):
		    sources elevation from a point-query API hosted by USGS
		or
		'arnuad-server':
		    sources elevation values from a raster database stored on arnaud

		NOTES: 	- Both sources are technically the same USGS 1/3 arc-second dataset.
			- However, slight variations in returned elevation values are likely.
			- Furthermore, there are performance differences between the sources.
			- Generally, we recommend selecting the USGS API for smaller queries
			  and arnaud for larger queries.

    Returns:
	A dictionary containing elevation, grade, and source information.

	ex:
	    grade_dictionary = {
			    'elevation' : (elev_val_1, elev_val_..., elev_val_n),
			    'grade' : (grade_val_1, grade_val_..., grade_val_n),
			    'source' : 'source name'
			    }
    """
    # get elevation values
    elev_tuple = elevation.get_elevation(coordinates, source=source)
     
    # get grade values
    grade_tuple = grade.get_grade(coordinates)

    # place both tuples in a dictionary
    gradeit_dict = {
                    'elevation' : elev_tuple,
                    'grade' : grade_tuple,
		    'source' : source,
                    }

    return gradeit_dict
