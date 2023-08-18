import unittest

import numpy as np
from gradeit import repo_root

from gradeit.coordinate import Coordinate
from gradeit.elevation.usgs_api import USGSApi
from gradeit.elevation.usgs_local import USGSLocal

LATS = np.linspace(39.702730, 39.695368, 10)
LONS = np.linspace(-105.245678, -105.209049, 10)
COORDS = [Coordinate.from_lat_lon(lat, lon) for lat, lon in zip(LATS, LONS)]


# Test the USGS Web API Implementation
class ElevTestApi(unittest.TestCase):
    @unittest.skip("Takes some time so skip by default")
    def test_api_no_filter(self):
        """
        Call the USGS Web API to append elevation at discrete points, do not
        filter the results
        """
        emodel = USGSApi()
        elevation_ft = emodel.get_elevation(COORDS)

        self.assertEqual(len(elevation_ft), len(COORDS))


class ElevTestRasterDB(unittest.TestCase):
    @unittest.skip("To run this, you'll have to download the raster tiles for Colorado")
    def test_raster_no_filter(self):
        """
        Test the raster database implementation
        """
        emodel = USGSLocal(repo_root() / "scripts/colorado_tiles")

        elevation_ft = emodel.get_elevation(COORDS)

        self.assertEqual(len(elevation_ft), len(COORDS))


if __name__ == "__main__":
    unittest.main(warnings="ignore")
