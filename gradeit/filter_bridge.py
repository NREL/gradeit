"""Module contains functionality associated with grade profiles."""

# NOTE: temporary for functon i/o testing
from numpy.random import randint
from math import radians, degrees, cos, sin, asin, atan2, sqrt
import pandas as pd
import numpy as np
#-----------------------------------------------------------------
def data_preproc (data):
    data_idx = data[0:-1]['grade_dec_unfiltered'].index
    id = []
    for i in data_idx: id.append(i)
    id.append(len(data))
    data['id'] = id
    #filtering 0 grade elements
    bridge_raw = data.loc[np.absolute(data['grade_dec_unfiltered']) < 0.0001]
    # bridge_raw = data.loc[np.absolute(data['elevation'])<0.00001]
    return bridge_raw

def bridge_segmentation(bridge_raw):
    # synthesize bridge data out of raw '0' grade values: distance <120
    idx = [[]]
    counter = 0
    c = 0
    for i in range(len(bridge_raw) - 1):
        if (bridge_raw['id'].iloc[i + 1] - bridge_raw['id'].iloc[i] == 1):  # we have consecutive points
            if counter == 0:
                idx.append([])
                # print('row appended')
                c += 1
            idx[c].append(i)
            counter = 1
        else:
            counter = 0
    idx.pop(0) #removing initial null element
    # extracting distance range from above data
    bridge = []
    for i in range(len(idx)):
        val = bridge_raw['cumulative_original_distance_ft'][idx[i][0]:idx[i][-1]]
        if len(val):
            bridge.append(val)
    return bridge

def bridge_filter_1(bridge, min_bridge_len):
    # removing short sections / artificial bridge
    pop_idx = []
    for i in range(len(bridge)):
        len_bridge = (bridge[i].iloc[-1] - bridge[i].iloc[0])
        # print("bridge" + str(i) + ": " + str(len_bridge))
        if len_bridge < min_bridge_len:
            pop_idx.append(i)
    for i in reversed(pop_idx):
        bridge.pop(i)
    return bridge

def bridge_extention(bridge, data, des_dist):
    # identifying boundaries of the bridge
    milesToft = 5280
    #des_dist = .8  # [in miles]
    des_dist *= milesToft  # [in feets]
    bridge_ext = []
    start_dist = []
    end_dist = []
    for i in range(len(bridge)):
        start_dist.append(bridge[i].iloc[0] - des_dist)
        end_dist.append(bridge[i].iloc[-1] + des_dist)
    for i in range(len(start_dist)):
        bridge_ext.append(data.loc[((data['cumulative_original_distance_ft'] > start_dist[i]) & (data['cumulative_original_distance_ft'] < end_dist[i]))])
    return(bridge_ext)

def bridge_filter_2(bridge_ext):
    # final filter based on bridge edges
    grade_max = 0.05 #max value of grade on the edge of bridge
    pop_idx_2 = []
    for i in range(len(bridge_ext)):
        if np.max(np.abs(bridge_ext[i]['grade_dec_unfiltered']) < grade_max):
            pop_idx_2.append(i)
    for i in reversed(pop_idx_2):
        bridge_ext.pop(i)
    return bridge_ext

def edge_trim(bridge_ext, data, general_filter):
    # Triming the grade of extended bridge
    final_idx = []
    for i in range(len(bridge_ext)):
        final_idx.append(bridge_ext[i].index)
        if general_filter:
            data.loc[final_idx[i][0]:final_idx[i][-1], 'grade_dec_filtered'] = 0
        else:
            data.loc[final_idx[i][0]:final_idx[i][-1], 'grade_dec_unfiltered'] = 0
    return data

def gradeCorrection_bridge (df, bridge_param):
    df_raw = data_preproc (df)
    df_bridge = bridge_segmentation(df_raw)
    df_bridge = bridge_filter_1(df_bridge, bridge_param[1])
    df_ext = bridge_extention(df_bridge, df, bridge_param[0])
    df_ext = bridge_filter_2(df_ext)
    df_final = edge_trim(df_ext, df, bridge_param[2])
    print('Bridge filter has been applied.')
    return df_final
