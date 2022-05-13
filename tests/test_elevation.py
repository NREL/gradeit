import unittest
import numpy as np
import pandas as pd

from gradeit import elevation


# Test the USGS Web API Implementation
class ElevTestApi(unittest.TestCase):
    def setUp(self):
        # Build a sample dataset with just 10 points for the no filter testing
        self.data = pd.DataFrame()
        self.data["lat"] = np.linspace(39.702730, 39.695368, 10)
        self.data["lon"] = np.linspace(-105.245678, -105.209049, 10)

        # The expected results are assigned to a class variable
        self.no_filter_desired_elevation_ft = np.array(
            [
                7048.15,
                7015.69,
                7157.89,
                7004.84,
                6921.27,
                6840.03,
                6696.7,
                6735.26,
                6554.42,
                6445.5,
            ]
        )

    def tearDown(self):
        pass

    def test_api_no_filter(self):
        """
        Call the USGS Web API to append elevation at discrete points, do not
        filter the results
        """
        self.data = elevation.usgs_api(
            self.data, sg_window=17, lat="lat", lon="lon", apply_filter=False
        )

        np.testing.assert_almost_equal(
            np.array(self.data["elevation_ft"]),
            self.no_filter_desired_elevation_ft,
            decimal=2,
        )


class ElevTestRasterDB(unittest.TestCase):
    def setUp(self):
        # Build a sample dataset with just 10 points for the no filter testing
        self.data = pd.DataFrame()
        self.data["lat"] = np.linspace(39.702730, 39.695368, 10)
        self.data["lon"] = np.linspace(-105.245678, -105.209049, 10)

        # The expected results are assigned to a class variable
        self.no_filter_desired_elevation_ft = np.array(
            [
                7048.15,
                7015.69,
                7157.89,
                7004.84,
                6921.27,
                6840.03,
                6696.7,
                6735.26,
                6554.42,
                6445.5,
            ]
        )

    @unittest.skip("TODO: need to add dummy raster data")
    def test_raster_no_filter(self):
        """
        Call the USGS Web API to append elevation at discrete points, do not
        filter the results
        """
        self.data = elevation.usgs_local_data(
            self.data, sg_window=17, lat="lat", lon="lon", filter=False
        )

        bool_out = np.allclose(
            np.array(self.data["elevation_ft"]),
            self.no_filter_desired_elevation_ft,
            atol=50,
        )  # 50 ft absolute tolerance

        self.assertTrue(bool_out)


if __name__ == "__main__":
    unittest.main(warnings="ignore")
