"""Module contains the primary functionality of GradeIT."""

from .elevation import get_elevation, elevation_filter
from .grade import get_grade

def gradeit(coordinates=None, vehicle_trip_data=None, elevation_source='usgs-api'):
    """
    A function that provides elevation and road grade values given coordinates or
    vehicle trip data.

    Parameters:
	coordinates:
	    nested lists/tuples that contain latitude and longitude floating-point
            coordinates.

            ex: Tuple of tuples of floats
                ((xx.xxxxxx, xxx.xxxxxx), (xx.xxxxxx, xxx.xxxxxx))

                or

                List of lists of floats
                [[lat_1, lon_1], [lat_2, lon_2]]

        vehicle_trip_data:
	    a dictionary containing the following keys and their associated values.
	    
	    keys:
	        'lat', 'lon', 'time_rel', 'gpsspeed', and 'elev_ft' (if available.)

	    NOTE:
	    If the 'elev_ft' key-value pair is provided with the vehicle_trip_data
	    dictionary, those values will be used to compute grade. Otherwise, 
	    elevation will be sourced using the selected elevation_source keyword arg.

	elevation_source:
	    valid keywords arguments are:
		
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
    # if no query was provided throw exception
    if coordinates is None and vehicle_trip_data is None:
        raise Exception(
	'''
	No query data provided.
	
	Please provide either coordinates in iterable form or
	vehicle trip data in dictionary form to the gradeit as
	a gradeit function keyword argument.
	'''
                       )

    # process a vehicle-trip-data-based query if vehicle data is provided
    elif vehicle_trip_data is not None:
        # if elevation has not been provided calculate it
        if not 'elev_ft' in vehicle_trip_data:
            coords = list(zip(vehicle_trip_data['lat'], vehicle_trip_data['lon']))
            vehicle_trip_data['elev_ft'] = get_elevation(coords,
                                                    source=elevation_source)

	# TODO: refactor elevation_filter function to remove responsibility for grade calculations
	# get the filtered elevation and grade from elevation_filter
        filtered_elev_tuple, filtered_grade_tuple = elevation_filter(vehicle_trip_data)

        gradeit_dict = {
		        'elevation (unfiltered)' : vehicle_trip_data['elev_ft'],
		        'elevation (filtered)' : filtered_elev_tuple,
			'grade (filtered)' : filtered_grade_tuple,
			'source' : elevation_source
			}

    # otherwise, process a coordinate-based query
    else:
        # get elevation values
        elev_tuple = get_elevation(coordinates, source=elevation_source)
     
        # get grade values
        distance_tuple, grade_tuple = get_grade(elev_tuple, coordinates=coordinates)

        # place both tuples in a dictionary
        gradeit_dict = {
                    'elevation (unfiltered)' : elev_tuple,
                    'distance (feet)':distance_tuple,
                    'grade (unfiltered)' : grade_tuple,
		    'source' : elevation_source,
                    }

    return gradeit_dict
