# The Road Grade Inference Tool (GradeIT) is used to append elevation and
# gradient information to GPS coordinates. Data can be a variety of locations
# where elevation and grade are desired, or a vehicle trip with a high frequency
# GPS signal.

# GradeIT functionality will be designed, demonstrated, and tested here

import unittest
import numpy as np
from ..gradeit import gradeit

class GradeitTest(unittest.TestCase):

    # Our user has GPS data along I-70 that they would like to append elevation
    # and grade information to
    def setUp(self):
        self.lats = np.linspace(39.702730, 39.695368, 50)
        self.lons = np.linspace(-105.245678, -105.209049, 50)
        self.coordinates = list(zip(lats,lons))

    def tearDown(self):
        pass

    def test_usgs_api(self):
        

if __name__ == '__main__':
    unittest.main(warnings='ignore') 