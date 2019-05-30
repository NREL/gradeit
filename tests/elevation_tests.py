import unittest
import numpy as np
import sys
sys.path.append('../')
import pandas as pd

from gradeit import elevation


class ElevTest(unittest.TestCase):
    
    def setUp(self):
        self.data = pd.DataFrame()
        self.data['lat'] = np.linspace(39.702730, 39.695368, 10)
        self.data['lon'] = np.linspace(-105.245678, -105.209049, 10)
        
    def tearDown(self):
        pass
    
    def test_usgs_api_elevation(self):
        coord_input = [self.data.lat[0],self.data.lon[0]]
        elev = elevation.usgs_api_elevation(coord_input)
        self.assertEqual(elev, 7048.15)
        
        coord_input = [self.data.lat[5],self.data.lon[5]]
        elev = elevation.usgs_api_elevation(coord_input)
        self.assertEqual(elev, 6840.03)
        
        coord_input = [self.data.lat[9],self.data.lon[9]]
        elev = elevation.usgs_api_elevation(coord_input)
        self.assertEqual(elev, 6445.5)
        
    def test_get_elevation_usgs(self):
        elev = elevation.get_elevation(self.data, 
                                lat_col = 'lat', 
                                lon_col = 'lon',
                                source = 'usgs-api')

        self.assertEqual(str(elev), '(7048.15, 7015.69, 7157.89, 7004.84, 6921.27, 6840.03, 6696.7, 6735.26, 6554.42, 6445.5)')
        
        
        
if __name__ == '__main__':
    unittest.main(warnings='ignore') 