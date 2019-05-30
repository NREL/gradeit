"""Module contains the primary functionality of GradeIT."""

from .elevation import get_elevation, elevation_filter
from .grade import get_grade

def gradeit(df = None, lat_col = 'lat', lon_col = 'lon', filtering = False, source = 'usgs-api'):
 
    # if no query was provided throw exception
    if df is None:
        raise Exception(
	'''
	No spatial data provided.
	
	Please provide a dataframe with latitude/longitude values 
    and the names of the columns containing that data.
	'''
                       )

    coordinates = list(zip(df[lat_col], df[lon_col]))
        
    if filtering == False:
        df['elevation_ft'] = get_elevation(coordinates, source=source)
        
        distance_ft, grade_dec = get_grade(tuple(df['elevation_ft'].values), coordinates=coordinates)
        
        df['distance_ft'] = distance_ft
        
        df['grade_dec'] = grade_dec
        
#     # process a vehicle-trip-data-based query if vehicle data is provided
#     elif vehicle_trip_data is not None:
#         # if elevation has not been provided calculate it
#         if not 'elev_ft' in vehicle_trip_data:
#             coords = list(zip(vehicle_trip_data['lat'], vehicle_trip_data['lon']))
#             vehicle_trip_data['elev_ft'] = get_elevation(coords,
#                                                     source=elevation_source)


#         filtered_elev_tuple, filtered_grade_tuple, filtered_cuml_dist, unfiltered_grade_tuple, unfiltered_cuml_dist = elevation_filter(vehicle_trip_data)

#         gradeit_dict = {
# 		        'elevation (unfiltered)' : vehicle_trip_data['elev_ft'],
# 		        'elevation (filtered)' : filtered_elev_tuple,
# 			'grade (filtered)' : filtered_grade_tuple,
#             'grade (unfiltered)' : unfiltered_grade_tuple,
#             'distance (filtered)' : filtered_cuml_dist,
#             'distance (unfiltered)' : unfiltered_cuml_dist,
# 			'source' : elevation_source
# 			}

#     # otherwise, process a coordinate-based query
#     else:
#         # get elevation values
#         elev_tuple = get_elevation(coordinates, source=elevation_source)
     
#         # get grade values
#         distance_tuple, grade_tuple = get_grade(elev_tuple, coordinates=coordinates)

#         # place both tuples in a dictionary
#         gradeit_dict = {
#                     'elevation (unfiltered)' : elev_tuple,
#                     'distance (feet)':distance_tuple,
#                     'grade (unfiltered)' : grade_tuple,
#                     'source' : elevation_source,
#                     }

    return df
