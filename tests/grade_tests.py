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
    
        self.data['elev_ft'] = [7051.126700732422, 7019.6391271875, 7166.562447382812, 6999.898018144531, 6919.229083066406, 6827.498526796875, 6672.75637855957, 6740.378447832031, 6551.383320751953, 6451.975711020507]
    
        self.distance = [1336.0892816, 1336.0892816, 1336.0892816, 1336.0892816, 1336.12209, 1336.12209, 1336.12209, 1336.12209, 1336.1548984]

        self.data['grade'] = [0.0, -0.0236, 0.11, -0.1247, -0.0604, -0.0687, -0.1158, 0.0506, -0.1415, -0.0744]

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
        
        self.assertEqual(dist_ft, self.distance)
    
    
    def test_get_grade(self):
        
        dist_out, grade_out = grade.get_grade(self.data.elev_ft, distances=self.distance)
    
        self.assertEqual(list(grade_out), list(self.data.grade))
            
if __name__ == '__main__':
    unittest.main(warnings='ignore') 