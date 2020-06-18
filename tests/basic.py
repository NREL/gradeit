import sys
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
sys.path.append('../')
from gradeit.gradeit import gradeit
from gradeit.filter_bridge import gradeCorrection_bridge
from gradeit.visualization import plot_data
# import gradeit.elevation as elevation

#############################################################################################
#User space
#############################################################################################
#import lat lon data for processing
data = pd.DataFrame()
#discretized lat/lon for testing
#data['lat'] = np.linspace(39.702730, 39.595368, 50)
#data['lon'] = np.linspace(-105.245678, -105.109049, 50)
#actual lat/lon for testing
df_truck = pd.read_csv('data/SF_bridge_trip_segment.csv')
data['lat']= df_truck['latitude']
data['lon']= df_truck['longitude']

#choose source: elevation data
api = False
local = True
if local: db_path= "C:/Users/amahbub/Documents/gradeit_old/NED_13/"

#choose filter option
general_filter = True
sg_val = 0 #Desired SG window # use 0 for default value

#choose bridge filter
bridge_filter = True
extention = 0.5 #in miles. extention around the edges of the bridge to be filtered
bridge_len = 2500 #in ft. minimum length of the bridge to be considered within the route
bridge_param = [extention, bridge_len, general_filter]


#choose plotting option
do_plot = True
plot_elevation = True
plot_grade = True
plot_param = np.append(plot_elevation, plot_grade)

#data saving
save_df = False
#################################################################################################
#Application space
#################################################################################################
# write grade info to csv file
def save_data(df):
    df.to_csv(r'file_name.csv', index=False)
    print("Data saved.")

if api:
    df_grade = gradeit(df=data, lat_col='lat', lon_col='lon', filtering=general_filter, source='usgs-api',des_sg = sg_val)
elif local:
    df_grade= gradeit(df=data, lat_col='lat', lon_col='lon', filtering=general_filter, source='usgs-local',
                                usgs_db_path=db_path, des_sg = sg_val)
print(df_grade.info())
if bridge_filter:df_grade = gradeCorrection_bridge (df_grade, bridge_param)
if do_plot: plot_data(df_grade, general_filter, plot_param)
if save_df : save_data(df_grade)
print("Process completed!")
#################################################################################################
