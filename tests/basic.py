import numpy as np
import sys
sys.path.append('../')
import pandas as pd

# import gradeit.elevation as elevation
from gradeit import elevation


data = pd.DataFrame()
data['lat'] = np.linspace(39.702730, 39.595368, 50)
data['lon'] = np.linspace(-105.245678, -105.109049, 50)

output = elevation.usgs_api(data, 
                            lat='lat', 
                            lon='lon', 
                            filter=False)

output_fltr = elevation.usgs_api(data, 
                            lat='lat', 
                            lon='lon', 
                            filter=True)

print(output)
print(output_fltr)