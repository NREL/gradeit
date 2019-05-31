import unittest
import numpy as np
import sys
sys.path.append('../')
import pandas as pd

from gradeit import grade

class GradeTest(unittest.TestCase):
    
    def setUp(self):
        self.data = pd.DataFrame()
        self.data['lat'] = np.linspace(39.702730, 39.695368, 10)
        self.data['lon'] = np.linspace(-105.245678, -105.209049, 10)
    
    
    def test_haversine_no_bearing(self):
                
        dist_km = grade.haversine(self.data.lat[0], 
                                  self.data.lon[0], 
                                  self.data.lat[1], 
                                  self.data.lon[1])
        
        self.assertEqual(dist_km, 0.40724)
        
        
    def test_haversine_bearing(self):
        
        dist_km, bearing = grade.haversine(self.data.lat[0], 
                                  self.data.lon[0], 
                                  self.data.lat[1], 
                                  self.data.lon[1],
                                  get_bearing=True)
        
        self.assertEqual(bearing, 104.64)
        
    
    def test_get_distances(self):
        coords = list(zip(self.data.lat, self.data.lon))
        dist_ft = grade.get_distances(coords)
        
        i70_expected = [1336.0892816, 1336.0892816, 1336.0892816, 1336.0892816, 1336.12209, 1336.12209, 1336.12209, 1336.12209, 1336.1548984]
        
        self.assertEqual(dist_ft, i70_expected)
    
    
    def test_get_grade()
    
            
if __name__ == '__main__':
    unittest.main(warnings='ignore') 