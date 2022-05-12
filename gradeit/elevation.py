"""
Append elevation to spatial data from a variety of sources including the USGS 
public API, and a local version of the same USGS 1/3 arc-second data in the 
form of a raster database.

Contributors: Jacob Holden, Cory Kennedy, Eric Wood, Evan Burton
"""

import requests
import numpy as np
from json import loads
from pathlib import Path
from matplotlib import pylab as mp
from scipy import stats
from scipy.interpolate import interp1d
from scipy import integrate
import scipy as sp
from scipy import signal
import warnings

import xarray as xr

warnings.simplefilter('ignore')
from .grade import get_grade, get_distances


def usgs_api(df, sg_window, lat='lat', lon='lon', filter=False):
    """
    Look up elevation for every location in a dataframe by latitude, longitude
    coordinates. The source for the data is the public USGS API, which compiles
    and serves data from the 1/3 arc-second Digital Elevation Model.

    More information is available at https://nationalmap.gov/epqs/
    """
    # print(df[lat], df[lon])
    # print(usgs_query_call(df[lat][0], df[lon][0]))
    df['elevation_ft'] = df.apply(lambda row: usgs_query_call(row[lat], row[lon]), axis=1)

    if filter == True:
        df = _elevation_filter(sg_window, df, lat=lat, lon=lon)

    return df


def usgs_query_call(lat, lon):
    """
    Build and run the query to the USGS API endpoint
    """

    URL = 'https://nationalmap.gov/epqs/pqs.php'
    lat = str(lat)
    lon = str(lon)
    UNITS = 'feet'
    OUTPUT = 'json'

    query = '{url}?x={lon}&y={lat}&units={units}&output={output}'.format(
        url=URL, lon=lon, lat=lat, units=UNITS, output=OUTPUT
    )
    response_json = requests.get(query)
    results = loads(response_json.text)  # a dict containing the json data
    elev = results['USGS_Elevation_Point_Query_Service'] \
        ['Elevation_Query'] \
        ['Elevation']
    elev = float(elev)

    return elev


def check_sg (sg_window, cumlDist):
    #compute the default value of SG window.
    avg_spd = cumlDist[-1]/len(cumlDist) #vehicle avg speed in ft/s
    filter_width = 2500 #in [ft], width of the spike to be filtered (tentative)
    filter_factor = 5
    polyorder = 3 #fixed value, do not change!
    df_filter = round(filter_width/avg_spd*filter_factor) #(estimated formula, change filter_width and filter_factor to get desired effect)
    if df_filter < polyorder: df_filter = polyorder + 2
    elif df_filter > len(cumlDist): df_filter = len(cumlDist) * 0.75 #safeguard against crossing sg array size
    sg_default = int(round(df_filter))
    if sg_default % 2 == 0: sg_default += 1 #if even, transform to odd
    print("Default SG computed: "+ str(sg_default))
    ####################################################
    # user inputs 0 to access the default value (see basic.py)
    if sg_window == 0:
        print("Default SG window applied: "+ str(sg_default))
        return sg_default
    else:
        #checks the validility of the user defined window
        if sg_window % 2 == 0:
            sg_window += 1
            print("SG window cannot be an even number.")
            print("SG window modified: "+ str(sg_window))
        if (sg_window > len(cumlDist)) or (sg_window < 3): #sg_window must be greater than polyorder = 3 and less than df size
            sg_window = sg_default
            print("SG window provided is greater than list length or less than polyorder.")
            print("Default SG window applied: " + str(sg_default))
        return sg_window


def _elevation_filter(sg_window, df, lat='lat', lon='lon'):
    """
    This implementation applies the SG filter in the temporal domain
    as opposed to the spatial domain. Filtering spatially requires 
    error-proned resampling of the elevation signal to match a uniform
    distance between each point. 
    """

    coordinates = list(zip(df[lat], df[lon]))
    distances = get_distances(coordinates)
    cuml_dist = np.append(0, np.cumsum(distances))

    # note: run final check on user SG value, provide default value if necessary
    sg_window = check_sg(sg_window, cuml_dist)
    
    # run SavGol filter
    elev_linear_sg = signal.savgol_filter(df['elevation_ft'], window_length=sg_window, polyorder=3)

    df['cumulative_original_distance_ft'] = cuml_dist
    df['elevation_ft_filtered'] = elev_linear_sg

    return df


def usgs_local_data(df, usgs_db_path, sg_window, lat='lat', lon='lon', filter=False):
    """
    Look up elevation for every location in a dataframe by latitude, longitude 
    coordinates. The source data is a locally downloaded raster database 
    containing the USGS 1/3 arc-second Digital Elevation Model.
    """

    coordinates = list(zip(df[lat], df[lon]))
    df['elevation_ft'] = get_raster_elev_profile(coordinates, usgs_db_path)

    if filter:
        df = _elevation_filter(sg_window, df, lat=lat, lon=lon)

    return df


def get_raster_elev_profile(coordinates, usgs_db_path):
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
    ts_full = []  # track query order
    grid_refs = build_grid_refs(lats, lons)
    unique_grid_refs = list(set(grid_refs))
    row_col = range(0, len(lons))

    # for each unique grid reference, find associated order, lat, lon, and elevation
    for uniq_ref in unique_grid_refs:
        ts = [row_col[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lats = [lats[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lons = [lons[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        elevation = get_raster_elev_data(uniq_ref, grid_lats, grid_lons, usgs_db_path)
        elevation_full += elevation
        ts_full += ts

    # reorder the elevation values to match the order of the query coordinates
    ts_full, elevation_full = [list(x) for x in zip(*sorted(zip(ts_full, elevation_full), key=lambda pair: pair[0]))]

    return elevation_full


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
    data = xr.open_rasterio(raster_path)

    geotransform = data.transform
    xOrigin = geotransform[2]
    yOrigin = geotransform[5]
    pixelWidth = geotransform[0]
    pixelHeight = geotransform[4]
    bands = len(data.band) 

    return xOrigin, yOrigin, pixelWidth, pixelHeight, bands, data


def get_raster_elev_data(grid_ref, lats, lons, usgs_db_path):
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
    # db_path = Path("/backup/mbap_shared/NED_13/") # Path from pathlib lbrary
    # db_path = Path("/Volumes/ssh/backup/mbap_shared/NED_13/")
    db_path = Path(usgs_db_path)

    # path from database top level down to raster file
    sub_path = Path() / 'grid' / grid_ref / ('grd' + grid_ref + '_13')  # Path from pathlib
    # complete path
    raster_path = Path(db_path / sub_path / "w001001.adf")  # Path from pathlib

    # if the raster path doesn't get exist, throw an exception
    if not raster_path.exists():  # Path from pathlib
        error_msg = '''Invalid file path provided.
	'{path}' does not exist.'''.format(path=raster_path)
        raise Exception(error_msg)

    (xOrigin, yOrigin, pixelWidth, pixelHeight,
        bands, data) = get_raster_metadata_and_data(raster_path)
    xOffset = [int((v - xOrigin) / pixelWidth) if v < 0.0 else 'nan' for v in np.float64(lons)]
    yOffset = [int((v - yOrigin) / pixelHeight) if v > 0.0 else 'nan' for v in np.float64(lats)]

    for val in range(len(lons)):
        if xOffset[val] == 'nan':
            # print 'passed'
            elevation += [np.nan]
        else:

            for i in range(bands):
                try:
                    raster_data = data[i, yOffset[val], xOffset[val]]
                except IndexError:
                    elevation.append(np.nan)

                elev_ft = float(raster_data) * 3.28084
                elevation.append(elev_ft)
                        
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
            val = str(int(abs(lons[i])) + 1)
            if len(val) < 3:
                val = '0' + val
            grid_refs += ['n' + str(int(abs(lats[i])) + 1) + 'w' + val]
        else:
            grid_refs += ['0']
    return grid_refs
