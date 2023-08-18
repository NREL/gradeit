# %%
import pandas as pd

from gradeit import repo_root
from gradeit.gradeit import gradeit

# %%
example_trace = pd.read_csv(repo_root() / "examples/data/sample_trip_1.csv")

# %%
example_trace.head()

# %%

# choose source for elevation data;
# this defaults to the USGS Local option, which requires you download the USGS raster tiles;
# see the scripts/get_usgs_tiles.py script to download tiles;
# sample traces 1, 2, and 3 are in the state of Colorado and so you can use the colorado_tiles.txt
# file as an input to the script

source = "usgs-local"  # options: 'usgs-api', 'usgs-local'

# if using the usgs-local option, you must provide the path to the local raster tiles
db_path = repo_root() / "scripts/colorado_tiles"

# should we filter the elevation data?
elevation_filter = True

# %%
df_w_grade = gradeit(
    df=example_trace,
    lat_col="latitude",
    lon_col="longitude",
    filtering=elevation_filter,
    source=source,
    usgs_db_path=db_path,
)
# %%
df_w_grade.head()
# %%
df_w_grade.elevation_ft.plot()
# %%
df_w_grade.elevation_ft_filtered.plot()
# %%
df_w_grade.grade_dec_unfiltered.plot()
# %%
df_w_grade.grade_dec_filtered.plot()
# %%
