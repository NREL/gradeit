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

        self.check_usgs_df = pd.DataFrame()
        self.check_usgs_df = self.data.copy()
        self.check_usgs_df['elevation_ft'] = [7048.15, 7015.69, 7157.89, 7004.84, 6921.27, 6840.03, 6696.7, 6735.26, 6554.42, 6445.5]
        self.check_usgs_df['distance_ft'] = [0, 1336.0892816, 1336.0892816, 1336.0892816, 1336.0892816, 1336.12209, 1336.12209, 1336.12209, 1336.12209, 1336.1548984]
        self.check_usgs_df['grade_dec'] = [0.0, -0.0243, 0.1064, -0.1146, -0.0625, -0.0608, -0.1073, 0.0289, -0.1353, -0.0815]

    def tearDown(self):
        pass

    def test_usgs_api_no_filter(self):
        
        self.data = gradeit.gradeit(self.data,
                        lat_col = 'lat',
                        lon_col = 'lon',
                        filtering = False,
                        source = 'usgs-api')
        
        pd.testing.assert_frame_equal(self.data, self.check_usgs_df)

    
    def test_raster_db_no_filter(self):
        
        self.data = gradeit.gradeit(self.data,
                        lat_col = 'lat',
                        lon_col = 'lon',
                        filtering = False,
                        source = 'arnaud-server')

        print(self.data)
        
        # pd.testing.assert_frame_equal(self.data, self.check_usgs_df)
        

if __name__ == '__main__':
    unittest.main(warnings='ignore') 