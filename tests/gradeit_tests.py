# The Road Grade Inference Tool (GradeIT) is used to append elevation and
# gradient information to GPS coordinates. Data can be a variety of locations
# where elevation and grade are desired, or a vehicle trip with a high frequency
# GPS signal.

# GradeIT functionality will be designed, demonstrated, and tested here

import unittest
import numpy as np
import sys
sys.path.append('../')
import pandas as pd

from gradeit import gradeit

class GradeitTest(unittest.TestCase):

    # Our user has GPS data along I-70 that they would like to append elevation
    # and grade information to
    def setUp(self):
        
        self.data = pd.DataFrame()
        self.data['lat'] = np.linspace(39.702730, 39.695368, 10)
        self.data['lon'] = np.linspace(-105.245678, -105.209049, 10)

    def tearDown(self):
        pass

    def test_usgs_api_no_filter(self):
        
        self.data = gradeit.gradeit(self.data,
                        lat_col = 'lat',
                        lon_col = 'lon',
                        filtering = False,
                        source = 'usgs-api')
        
        print(self.data)
        

if __name__ == '__main__':
    unittest.main(warnings='ignore') 