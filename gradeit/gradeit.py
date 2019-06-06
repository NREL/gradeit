"""Module contains the primary functionality of GradeIT."""

from gradeit import elevation
from gradeit import grade

def gradeit(df = None, lat_col = 'lat', lon_col = 'lon', filtering = False, source = 'usgs-api'):
 


    coordinates = list(zip(df[lat_col], df[lon_col]))
        
    # Run the appropriate elevation function based on user's desired data source
    if source == 'usgs-api':
        
        df = elevation.usgs_api(df,
                               lat=lat_col,
                               lon=lon_col,
                               filter=filtering)
        
    elif source == 'usgs-local':
        
        df = elevation.usgs_local_data(df,
                                       lat=lat_col,
                                       lon=lon_col,
                                       filter=filtering)
    
    else:
        raise Exception(
        '''
        Invalid elevation data source provided.
        
        Provide one of these options: ['usgs-api','usgs-local']
        '''
        )
        
    # Cases where filtering is desired return both filtered and unfiltered results
    # Select the filtered elevation data for grade derivation
    if filtering == True:
        elev_arr = df['elevation_ft_filtered'].values
    else:
        elev_arr = df['elevation_ft'].values

    distance_ft, grade_dec = grade.get_grade(elev_arr, coordinates=coordinates)

    df['distance_ft'] = [0] + list(distance_ft)

    df['grade_dec'] = grade_dec


    return df
