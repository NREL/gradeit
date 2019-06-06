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

class GradeitTests(unittest.TestCase):
    
    # Load desired solution CSVs from /tests/.data directory
    # Solutions are for both 10 point sequence on I-70 and 150 point drive cycle sample
    def setUp(self):
        self.data = pd.DataFrame()
        self.data['lat'] = np.linspace(39.702730, 39.695368, 10)
        self.data['lon'] = np.linspace(-105.245678, -105.209049, 10)
        
        self.unfiltered_api_desired_df = pd.read_csv('.data/i70_10pnts_INTEGRATED_SOLUTION.csv')
        
        self.data_drvcyc = pd.read_csv('.data/caltrans_drvCycle_2345470_1_150pnts.csv')

        self.filter_api_desired_df = pd.read_csv('.data/caltrans_drvCycle_2345470_1_150pnts_INTEGRATION_SOLUTION.csv')
        
        self.unfiltered_local_desired_df = pd.read_csv('.data/i70_10pnts_usgs-local_INTEGRATED_SOLUTION.csv')

        self.filter_local_desired_df = pd.read_csv('.data/caltrans_drvCycle_2345470_1_150pnts_usgs-local_INTEGRATION_SOLUTION.csv')
    
    def test_usgs_api_no_filter(self):
        df_result = gradeit.gradeit(df=self.data,
                                    lat_col='lat',
                                    lon_col='lon',
                                    filtering=False,
                                    source='usgs-api')
        
        pd.testing.assert_frame_equal(df_result, self.unfiltered_api_desired_df)
        
    
    def test_usgs_api_with_filter(self):
        df_result = gradeit.gradeit(df=self.data_drvcyc,
                                    lat_col='lat',
                                    lon_col='lon',
                                    filtering=True,
                                    source='usgs-api')
        
        pd.testing.assert_frame_equal(df_result, self.filter_api_desired_df)
        
        
    def test_usgs_local_no_filter(self):
        df_result = gradeit.gradeit(df=self.data,
                                    lat_col='lat',
                                    lon_col='lon',
                                    filtering=False,
                                    source='usgs-local')
        
        pd.testing.assert_frame_equal(df_result, self.unfiltered_local_desired_df)
        
    
    def test_usgs_local_with_filter(self):
        df_result = gradeit.gradeit(df=self.data_drvcyc,
                                    lat_col='lat',
                                    lon_col='lon',
                                    filtering=True,
                                    source='usgs-local')
        
        pd.testing.assert_frame_equal(df_result, self.filter_local_desired_df)


if __name__ == '__main__':
    unittest.main(warnings='ignore') 
