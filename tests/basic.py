import sys
import numpy as np
import pandas as pd
import time

from gradeit.gradeit import gradeit

sys.path.append('../')

# import gradeit.elevation as elevation

data = pd.DataFrame()
data['lat'] = np.linspace(39.702730, 39.595368, 50)
data['lon'] = np.linspace(-105.245678, -105.109049, 50)

# output = elevation.usgs_api(data, 
#                             lat='lat', 
#                             lon='lon', 
#                             filter=False)

# output_fltr = elevation.usgs_api(data, 
#                             lat='lat', 
#                             lon='lon', 
#                             filter=True)

# output_raster = elevation.usgs_local_data(data,
#                                           lat='lat',
#                                           lon='lon',
#                                           filter=False)
# t1 = time.time()
# df_api = gradeit(df=data, lat_col='lat', lon_col='lon', filtering=False, source='usgs-api')
# t2 = time.time()
# print('API time: ', t2-t1)

t3 = time.time()
df_local = gradeit(df=data, lat_col='lat', lon_col='lon', filtering=False, source='usgs-local',
                   usgs_db_path="/Volumes/ssh/backup/mbap_shared/NED_13/")
t4 = time.time()

print('Local time: ', t4-t3)
# print(output)
# print(output_fltr)
print(df_local)
