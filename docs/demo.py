#!/usr/bin/env python
# coding: utf-8

# %%
import numpy as np
import pandas as pd
import time

from gradeit.gradeit import gradeit

# %% [markdown]
# ## Quick Start
#
# If you only 10's or 100's of GPS points requiring elevation and grade, GradeIT can point to the USGS web-api to obtain raw elevation information.
# This allows the user to run GradeIT "out-of-the-box" without accessing any supplemental data.
# However, the web-api is rate limited and network latency can slow the process quite a bit, __so this method is not advised for greater than ~100 points__.
#
# In the resulting dataframe, the user is like most interested in the ```elevation_ft_filtered``` and ```grade_dec_filtered``` columns.

# %%
start = time.time()
# sample data
data = pd.DataFrame()
data["lat"] = np.linspace(39.702730, 39.595368, 20)
data["lon"] = np.linspace(-105.245678, -105.109049, 20)

# append elevation and grade from the USGS web-api
df_grade = gradeit(
    df=data, lat_col="lat", lon_col="lon", filtering=True, source="usgs-api"
)
end = time.time()
print(f"Time elapsed: {end-start} seconds")

# %%
df_grade.head()

# %% [markdown]
# ## Improved Performance
#
# GradeIT can obtain raw elevation data from the USGS web-api, but this can be quite slow and has severe limitations if the user is appending elevation and grade data to a large dataset.
# A better option is to point GradeIT to a local version of the USGS raster database.
# The full database is ~500GB, so it is not convenient or advisable to try to store this on a laptop, but rather a network storage location or a high-performance computer.
#
# In this example, I have just copied the specific tile from the raster DB to my local machine (a bit of a hack).
# Note that elevation and grade are being appended for an order of magnitude more points here and it takes under 1 second, compared to over 10 seconds using the web-api with an order of magnitude few points.
# The main project [README](https://github.com/NREL/gradeit) provides a link to USGS data available for download. - at this time, documentation is lacking for how to replicate your own local database,
# feel free to open an issue if you have a project need and GradeIT contributors will be happy to help.

# %%
raster_path = "../raster-local/NED_13/"

# sample data
data = pd.DataFrame()
data["lat"] = np.linspace(39.702730, 39.595368, 200)
data["lon"] = np.linspace(-105.245678, -105.109049, 200)


df_grade = gradeit(
    df=data,
    lat_col="lat",
    lon_col="lon",
    filtering=True,
    source="usgs-local",
    usgs_db_path=raster_path,
)
