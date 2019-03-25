"""
Module contains functionality associated with elevation profiles.

Author: Cory Kennedy

Credits: A number of the functions in this moduel are derived from
	previous work by Eric Burton
"""

import requests
import numpy as np
from json import loads
from os import path
from pathlib import Path
from gdal import Open

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

    # get each elevation value from USGS API
    for coord in coordinates:

        # query USGS API and store resulting elevation
        elev = usgs_api_elevation(coord)
        # append elevation to the elevations list
        elevations += [elev]

    return tuple(elevations)


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

    # cast value to a float
    elev = float(elev)

    return elev


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
    data = Open(raster_path) # Open function from GDAL
    # if raster data returns as None, raise an exception
    # NOTE: returning NoneType values is GDAL's way of raising exceptions
    if data is None:
        #print 'Grid Does not Exist'
        #xOrigin = None
        #yOrigin = None
        #pixelWidth = None
        #pixelHeight = None
        #bands = None
        #rows = None
        #cols = None
	if path.isfile(raster_path): # path from os library
	    error_msg = "GDAL could not open the raster file."
	else:
	    error_msg = "The file path provided does not point\
			    to a valid raster file."
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


def get_elev_data(grid_ref, lons, lats):
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
    sub_path = Path('grid' + grid_ref / 'grd' + grid_ref + '_13') # Path from pathlib
    # complete path
    raster_path = Path(db_path / sub_path / "w001001.adf") # Path from pathlib
    #raster_path = 'E:\\DEM_Database\\NED_13\\grid\\' + grid_ref + '\\' + sub_path + '\\w001001.adf'
    
    # if the raster path doesn't get exist, throw an exception
    if not path.exists(raster_path): # path from os library
	error_msg = '''Invalid file path provided.
	'{path}' does not exist.'''.format(path=raster_path)
        raise Exception(error_msg)

    # otherwise, get the raster metadata and data
    else:
	# TODO place this function call in a try-catch
        (xOrigin, yOrigin, pixelWidth, pixelHeight,\
	bands, rows, cols, data) = get_raster_metadata_and_data(raster_path)
        xOffset = [int((v - xOrigin) / pixelWidth) if v < 0.0 else 'nan' for v in np.float64(lons)]
        yOffset = [int((v - yOrigin) / pixelHeight) if v > 0.0 else 'nan' for v in np.float64(lats)]
        
	for val in range(len(lons)):
	    if xOffset[val] == 'nan':
                #print 'passed'
                elevation.append(np.nan)
            else:

                for i in range(bands):
                    band = data.GetRasterBand(i+1) # 1-based index
                    raster_data = band.ReadAsArray(xOffset[val], yOffset[val], 1, 1)
                    if raster_data is not None:
                        ele = float(raster_data[0,0]) * 3.28084
                        elevation.append(ele)
                    else:
                        #print 'passed'
                        elevation.append(np.nan)
        del data
    return elevation


def build_grid_refs(lons, lats):
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
            val = str(int(abs(lons[i])))+1)
            if len(val) < 3:
                val = '0' + val
            grid_refs.append('n' + str(int(abs(lats[i]))+1) + 'w' + val)
        else:
            grid_refs.append('0')
    return np.array(grid_refs)


def return_elevation_profiles(lats, lons):
    """
    This function takes latitude and longitude values and returns an
    elevation profile from the raster database on the Arnaud server.

    Parameters:
    	Two iterables (list, tuple, or numpy array.) The first containing
	latitude float values, and the second longitude float values.
    Return value:
    	A numpy array of elevation float values from the raster database.
    """
    if type(lons) == list or type(lons) == tuple:
        lons = np.array(lons)
        lats = np.array(lats)
    
    elevation_full = []
    ts_full = []
    grid_refs = build_grid_refs(lons, lats)
    unique_grid_refs = list(set(grid_refs))
    row_col = range(0, len(lons))

    for ref in unique_grid_refs:
        ts = row_col[(grid_refs == ref)]
        elevation = get_elev_data(ref, lons[(grid_refs == ref)], lats[(grid_refs == ref)])
        elevation_full += list(elevation)
        ts_full += list(ts)

    ts_full, elevation_full = [list(x) for x in zip(*sorted(zip(ts_full, elevation_full), key=lambda pair: pair[0]))]
    elevation_full = np.array(elevation_full)
    
    return elevation_full
