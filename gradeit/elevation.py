"""
Module contains functionality associated with elevation profiles.

Author: Cory Kennedy
Date: Mar 2019
Credits: A number of the raster database related functions in this module are
	derived from previous work by Evan Burton (circa 2014)
"""

import requests
import numpy as np
from json import loads
from pathlib import Path
from gdal import Open
from matplotlib import pylab as mp
from scipy import stats
from scipy.interpolate import interp1d
from scipy import integrate
import scipy as sp
from scipy import signal
import warnings
warnings.simplefilter('ignore')
from .grade import get_grade, get_distances

def get_elevation(coordinates_df, lat_col, lon_col, source='usgs-api'):
    """
    A function that provides elevation values given coordinates

    Parameters:
    	coordinates:
            nested lists/tuples that contain latitude and longitude floating-point
            coordinates.
        	
	    ex:	Tuple of tuples of floats
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
        A tuple containing floating-point elevation values.

        ex:
            Tuple of floats
            (xxxx.xx, elev_2, elev_3, ...)
    """
    # check source keyword argument
    if source not in ['arnaud-server', 'usgs-api']:
        error_msg = '''Invalid keyword argument for keyword 'source'
	Valid arguments are: source='arnaud-server' or source='usgs-api'''
        raise ValueError(error_msg)

    coordinates = list(zip(coordinates_df[lat_col], 
                           coordinates_df[lon_col]))
        
    if source == 'usgs-api':
        elevations = []
        # get each elevation value from USGS API        
        for coord in coordinates:
            # query USGS API and store resulting elevation
            elev = usgs_api_elevation(coord)
            # append elevation to the elevations list
            elevations += [elev]
        return tuple(elevations)

    if source == 'arnaud-server':
        elevations = get_raster_elev_profile(coordinates)
        return elevations


####### USGS API access function ######

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
    elev = float(elev)

    return elev


###### Raster database access functions ######

def get_raster_metadata_and_data(raster_path):
    """
    A function that queries the USGS raster database on the Arnaud server
    (/backup/mbap_shared/NED_13/) and returns the elevation values and
    metadata associated with the raster grid at the provided raster path.

    Parameters:
	a file path string to the raster grid file containing elevation values
	of interest
    Returns:
    	a tuple containing the following metadata and data
    	(Origin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data)
    """
    data = Open(raster_path.as_posix()) # Open function from GDAL
    # if raster data returns as None, raise an exception
    # NOTE: returning NoneType values is GDAL's way of raising exceptions
    if data is None:
        if raster_path.is_file(): # Path from pathlib
            error_msg = "GDAL could not open the raster file."
        else:
            error_msg = "The file path provided does not point to a valid raster file."
        
        raise Exception(error_msg)

    # otherwise, GDAL successfully opened the raster file, return the data
    else:
        #print 'Geotransform Elevation Data'
        geotransform = data.GetGeoTransform()
        xOrigin = geotransform[0]
        yOrigin = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        #print 'Unpack Grid'
        data.ReadAsArray()
        cols = data.RasterXSize
        rows = data.RasterYSize
        bands = data.RasterCount
        #print 'Grid Unpack Complete'

    return (xOrigin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data)

def get_raster_elev_data(grid_ref, lats, lons):
    """
    A function that specifies the path to the raster database, calls
    get_raster_metadata_and_data(raster_path), processes the results
    from raster data into geo-referenced, human-readable, elevation data.

    Parameters:
	a grid refernce ID string, an iterable of longitude float values,
	and an iterable of latitude float values
	float value that mark the position of the elevation query
    Returns:
    	a list of floats containing elevation values
    """
    elevation = []
   
    # path to arnaud's raster database
    db_path = Path("/backup/mbap_shared/NED_13/") # Path from pathlib lbrary
    # path from database top level down to raster file
    sub_path = Path() / 'grid' / grid_ref / ('grd' + grid_ref + '_13') # Path from pathlib
    # complete path
    raster_path = Path(db_path / sub_path / "w001001.adf") # Path from pathlib
    
    # if the raster path doesn't get exist, throw an exception
    if not raster_path.exists(): # Path from pathlib
        error_msg = '''Invalid file path provided.
	'{path}' does not exist.'''.format(path=raster_path)
        raise Exception(error_msg)

    # otherwise, get the raster metadata and data
    else:
        (xOrigin, yOrigin, pixelWidth, pixelHeight,\
	bands, rows, cols, data) = get_raster_metadata_and_data(raster_path)
        xOffset = [int((v - xOrigin) / pixelWidth) if v < 0.0 else 'nan' for v in np.float64(lons)]
        yOffset = [int((v - yOrigin) / pixelHeight) if v > 0.0 else 'nan' for v in np.float64(lats)]
        
        for val in range(len(lons)):
            if xOffset[val] == 'nan':
                #print 'passed'
                elevation += [np.nan]
            else:

                for i in range(bands):
                    band = data.GetRasterBand(i+1) # 1-based index
                    raster_data = band.ReadAsArray(xOffset[val], yOffset[val], 1, 1)
                    if raster_data is not None:
                        elev_ft = float(raster_data[0,0]) * 3.28084
                        elevation += [elev_ft]
                    else:
                        #print 'passed'
                        elevation += [np.nan]
        del data
    return elevation

def build_grid_refs(lats, lons):
    """
    This function takes latitude and longitude values and returns
    grid reference IDs that are used as keys for raster grid files
    
    Parameters:
    	Two iterables containing float values. The first containing
	latitudes, and the second containing longitudes.
    Return value:
    	A numpy array of grid reference ID strings.
    """
    grid_refs = []
    for i in range(len(lons)):
        if lats[i] > 0.0 and lons[i] < 0.0:
            val = str(int(abs(lons[i]))+1)
            if len(val) < 3:
                val = '0' + val
            grid_refs += ['n' + str(int(abs(lats[i]))+1) + 'w' + val]
        else:
            grid_refs += ['0']
    return grid_refs

def get_raster_elev_profile(coordinates):
    """
    This function takes latitude and longitude values, of coordinate pairs
    and returns an elevation profile from the raster database on the
    arnaud server.

    Parameters:
    	an iterable of iterables (list of lists, tuple of tuples, etc.)
	ex:    [[lat1, lon1], [lat2, lon2]]
    Return value:
    	A list of elevation float values from the raster database.
    """
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]
    elevation_full = []
    ts_full = [] # track query order
    grid_refs = build_grid_refs(lats, lons)
    unique_grid_refs = list(set(grid_refs))
    row_col = range(0, len(lons))

    # for each unique grid reference, find associated order, lat, lon, and elevation
    for uniq_ref in unique_grid_refs:
        ts = [row_col[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lats = [lats[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lons = [lons[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        elevation = get_raster_elev_data(uniq_ref, grid_lats, grid_lons)
        elevation_full += elevation
        ts_full += ts

    # reorder the elevation values to match the order of the query coordinates
    ts_full, elevation_full = [list(x) for x in zip(*sorted(zip(ts_full, elevation_full), key=lambda pair: pair[0]))]
    
    return elevation_full
    
def elevation_filter(pnts):
   
    # resample uniformly
    if 'distance (feet)' in pnts.keys():
        cuml_dist = np.append(0,np.cumsum(pnts['distance (feet)']))
    else:
        coordinates = list(zip(pnts['lat'],pnts['lon']))
        cuml_dist = np.append(0,np.cumsum(get_distances(coordinates)))
        
    flinear = sp.interpolate.interp1d(cuml_dist, pnts['elev_ft'] )

    xnew = np.linspace(cuml_dist[0], cuml_dist[-1], len(cuml_dist))
    elev_linear = flinear(xnew)
    
    # run SavGol filter
    elev_linear_sg = signal.savgol_filter(elev_linear, window_length=17, polyorder=3)
    
    # return grade values
    filter_grade = get_grade(elev_linear_sg, distances = np.diff(xnew))[1]
    unfilter_grade = get_grade(pnts['elev_ft'], distances = np.diff(cuml_dist))[1]
    
    return tuple(elev_linear_sg), tuple(filter_grade), tuple(xnew), tuple(unfilter_grade), tuple(cuml_dist)
    
    
