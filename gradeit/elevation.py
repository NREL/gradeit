"""
Module contains functionality associated with elevation profiles.

Author: Cory Kennedy
Date: Mar 2019
Credits: A number of the raster database related functions in this module are
	derived from previous work by Eric Burton (circa 2014)
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
import warnings
warnings.simplefilter('ignore')
from .grade import get_grade

def get_elevation(coordinates, source='usgs-api'):
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
    if source not in set(['arnaud-server', 'usgs-api']):
        error_msg = '''Invalid keyword argument for keyword 'source'
	Valid arguments are: source='arnaud-server' or source='usgs-api'''
        raise ValueError(error_msg)

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
    # TODO: refactor to eliminate any grade responsibility from the function

    time_sec = np.copy(pnts['time_rel'])
    speed_mph = np.copy(pnts['gpsspeed'])
    elevation_ft = np.copy(pnts['elev_ft'])
    functional_class = [1]*len(time_sec)

    bin_size_ft = 100.0
    window_size_list = [5,7,5,5,5,5]
    while_accept_val_lst = [9,3,5,5,9,9]

    t_s = np.asarray(time_sec)
    fc_ind = mp.find(np.equal(np.asarray(functional_class),None))
    func_class = np.asarray(functional_class)
    func_class[fc_ind] = 0
    wav_lst = np.zeros((len(t_s),1))
    for i in range(len(wav_lst)):
        wav_lst[i] = while_accept_val_lst[func_class[i]]

    dist_ft = 5280.0*integrate.cumtrapz(speed_mph, x=(t_s/3600.0) , initial=0)
    ## Down-sample the raw data at uniformly spaced points (by distance)
    dist_ft_uni, elev_ft_uni, func_class_uni, wav_lst_uni = get_uniform_data( dist_ft, elevation_ft, func_class, wav_lst, bin_size_ft )

    ## Smooth the elevation profile
    elev_ft_uni_new, elev_ft_uni_new_adj = smoothing_filter(elev_ft_uni, func_class_uni, window_size_list, bin_size_ft)

    ## Discard and backfill outlier points
    while_cnt = 0
    retention_index_prev = np.asarray(range(len(elev_ft_uni_new_adj)))
    no_change = 0
    while np.any(np.greater(abs(np.diff(elev_ft_uni_new_adj)),wav_lst_uni[1:])) and no_change==0:
        while_cnt += 1
        test_values = np.diff(elev_ft_uni_new_adj)
        test_values = np.insert(test_values, 0, 0)
        retention_index = mp.find( np.greater(wav_lst_uni,abs(test_values)) )
        if retention_index[0] is not 0:
            retention_index = np.insert(retention_index, 0, 0)
        if retention_index[-1] is not len(elev_ft_uni_new_adj)-1:
            retention_index = np.append(retention_index, len(elev_ft_uni_new_adj)-1)

        retention_index = np.intersect1d(retention_index,retention_index_prev)
        if np.array_equal(retention_index,retention_index_prev):
            no_change=1
        retention_index_prev = np.copy(retention_index)

        elev_ft_func = interp1d(dist_ft_uni[retention_index], elev_ft_uni[retention_index], kind=1)
        elev_ft_uni = elev_ft_func(dist_ft_uni)
        elev_ft_uni_new, elev_ft_uni_new_adj = smoothing_filter(elev_ft_uni, func_class_uni, window_size_list, bin_size_ft)

    ## Interpolate on the smoothed elevation profile at the original distance points
    if len(dist_ft_uni) > 1:
        new_elev_ft_func = interp1d(dist_ft_uni, elev_ft_uni_new, kind=1)
        new_elev_ft = new_elev_ft_func(dist_ft)
    else:
        filtered_elev_ft  = elevation_ft
    # TODO: refactor to eleminate any grade responsibility from the elevation module
    filtered_grade = get_grade(filtered_elev_ft, distances=dist_ft)

    # Calculate error (deviation) from old and new elevation series
    # elev_filter_error = np.sum(np.absolute(new_elev_ft - elevation_ft))/len(elevation_ft)
    return tuple(filtered_elev_ft), tuple(filtered_grade)

def get_uniform_data(*args):

    # internally define variables
    dist_old = args[0]
    elev_old = args[1]
    func_class_old = args[2]
    wav_lst_old = args[3]
    nom_dist_window = args[4]

    window_cnt = mp.ceil(max(dist_old)/nom_dist_window)
    act_dist_window = max(dist_old)/window_cnt

    dist_new = mp.linspace(0.0, dist_old[-1], window_cnt+1)
    elev_new = np.asarray([-1.0]*len(dist_new))
    func_class_new = np.zeros(len(dist_new)) - 1.0
    wav_lst_new = np.zeros(len(dist_new)) - 1.0

    for i in range(len(dist_new)):
        logical1 = dist_old >= (dist_new[i]-act_dist_window/2.0)
        logical2 = dist_old <= (dist_new[i]+act_dist_window/2.0)
        ind = mp.find( np.bitwise_and(logical1, logical2) )
        if len(ind) is not 0:
            y0 = elev_old[ind]
            elev_new[i] = mp.median(y0)
            func_class_mode, func_class_mode_cnt = stats.mode( func_class_old[ind] )
            func_class_new[i] = np.copy(func_class_mode)
            wav_mode, wav_mode_cnt = stats.mode( wav_lst_old[ind] )
            wav_lst_new[i] = np.copy(wav_mode)

    elev_new[0] = 1.0*elev_old[0]
    elev_new[-1] = 1.0*elev_old[-1]

    ind = mp.find(elev_new is not -1.0)
    if len(ind) > 1:
        elev_new_func = interp1d( dist_new[ind], elev_new[ind], kind=1 )
        elev_new = elev_new_func(dist_new)

    ind = mp.find(func_class_new is not-1.0)
    if len(ind) > 1:
        fc_new_func = interp1d( dist_new[ind], func_class_new[ind], kind=0 )
        func_class_new = fc_new_func(dist_new)

    ind = mp.find(wav_lst_new is not -1.0)
    if len(ind) > 1:
        wav_new_func = interp1d( dist_new[ind], wav_lst_new[ind], kind=0 )
        wav_lst_new = wav_new_func(dist_new)

    return dist_new, elev_new, func_class_new, wav_lst_new


def smoothing_filter(*args):

    # internally define variables
    speed = args[0]
    fc_lst = args[1]
    window_cnt_lst = args[2]
    bin_size_ft = args[3]

    ### hold initial and final values at start and end of arrays
    buffer_data0 = np.asarray([speed[0]]*int((max(window_cnt_lst)-1)/2))
    buffer_data1 = np.asarray([speed[-1]]*int((max(window_cnt_lst)-1)/2))
    speed = np.insert(speed, [0]*len(buffer_data0), buffer_data0)
    speed = np.append(speed, buffer_data1)

    speed_adjustment = np.zeros( len(speed) )

    buffer_data0 = np.asarray([fc_lst[0]]*int((max(window_cnt_lst)-1)/2))
    buffer_data1 = np.asarray([fc_lst[-1]]*int((max(window_cnt_lst)-1)/2))
    fc_lst = np.insert(fc_lst, [0]*len(buffer_data0), buffer_data0)
    fc_lst = np.append(fc_lst, buffer_data1)

    # identify segments to convolve
    fc_lst_diff = np.diff(fc_lst)
    interval_end = np.asarray(mp.find(fc_lst_diff is not 0))
    interval_start = interval_end+1
    interval_end = np.append(interval_end, len(fc_lst)-1-int(max(window_cnt_lst)-1)/2)
    interval_start = np.insert(interval_start, 0, (max(window_cnt_lst)-1)/2)

    for fa in range(len(interval_start)):
        window = np.array([window_cnt_lst[int(fc_lst[interval_start[fa]])]])-1
        speed_sub0 = np.copy( speed[int(interval_start[fa]-window/2):int(interval_end[fa]+1+window/2)] )

        # determine number of points for filtering
        n_points = np.arange(0, window + 1)
        binomial_coefficients = []
        for i in n_points: # calculate binomial filter coefficients
            binomial_coefficients.append(float(np.math.factorial(window)/
            (np.math.factorial(window-i)*np.math.factorial(i))))

        binomial_coefficients =  np.divide(binomial_coefficients,
                                           np.sum(binomial_coefficients))

        # Determine the Savitsky Golay Filter Coefficients assuming 3 order
        order_range = range(3+1)
        b = np.mat([[k**i for i in order_range] for k in range(int(-1*window[0]/2), int(window[0]/2+1))])
        m = np.linalg.pinv(b).A[0]

        # perform the SG convolution on the speed data
        speed_sub = np.convolve(m, speed_sub0, mode = 'valid')

        # now that we have the binomial filter coefficients we can convolve the
        # speed data with the filter to get binomial filter smoothed values
        speed_sub = np.convolve(binomial_coefficients, np.r_[ speed_sub0[0:int(window/2)] , speed_sub , speed_sub0[len(speed_sub0)-int(window/2):] ], mode = 'valid')

        ### insert filtered speed subsegment back into complete array
        speed[interval_start[fa]:interval_end[fa]+1] = np.copy(speed_sub)
        speed_adjustment[int(interval_start[fa]):int(interval_end[fa]+1)] = speed_sub0[int(window/2):int(-window/2)] - speed_sub

    ### adjust elevation at intersection of smoothed segments
    for fa in range(len(interval_start)-1):
        gr0 = (speed[interval_end[fa]]-speed[interval_end[fa]-1]) / bin_size_ft
        gr1 = (speed[interval_start[fa+1]+1]-speed[interval_start[fa+1]]) / bin_size_ft
        avg_grd = (gr0+gr1) / 2.0
        target_trans_elev = speed[interval_end[fa]] + avg_grd*bin_size_ft
        elev_adj = target_trans_elev - speed[interval_start[fa+1]]
        speed[interval_start[fa+1]:] = speed[interval_start[fa+1]:] + elev_adj

    ## Remove buffer data on either end of array
    buff_len = len(buffer_data0)
    speed = speed[buff_len:-buff_len]
    speed_adjustment = speed_adjustment[buff_len:-buff_len]

    return speed, speed_adjustment


