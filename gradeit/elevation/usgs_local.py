from pathlib import Path
from typing import List, Union

import numpy as np
import rasterio as rio

from gradeit.coordinate import Coordinate
from gradeit.elevation.elevation_model import ElevationModel


class USGSLocal(ElevationModel):
    """
    An elevation model to look up elevation by latitude, longitude
    coordinates. The source data is a locally downloaded raster database
    containing the USGS 1/3 arc-second Digital Elevation Model.
    """

    usgs_db_path: Path

    def __init__(self, usgs_db_path: Union[Path, str]):
        self.usgs_db_path = Path(usgs_db_path)

    def get_elevation(self, trace: List[Coordinate]) -> List[float]:
        elevation = get_raster_elev_profile(trace, self.usgs_db_path)

        return elevation


def get_raster_elev_profile(coordinates: List[Coordinate], usgs_db_path):
    """
    This function takes latitude and longitude values, of coordinate pairs
    and returns an elevation profile from the raster database on the
    arnaud server.

    Parameters:
        an iterable of iterables (list of lists, tuple of tuples, etc.)
        ex:    [[lat1, lon1], [lat2, lon2]]
    Return value:
        A list of elevation float values from the raster database.
    """
    lats = [coord.latitude for coord in coordinates]
    lons = [coord.longitude for coord in coordinates]
    elevation_full = []
    ts_full = []  # track query order
    grid_refs = build_grid_refs(lats, lons)
    unique_grid_refs = list(set(grid_refs))
    row_col = range(0, len(lons))

    # for each unique grid reference, find associated order, lat, lon, and elevation
    for uniq_ref in unique_grid_refs:
        ts = [row_col[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lats = [lats[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        grid_lons = [lons[i] for i in range(len(grid_refs)) if grid_refs[i] == uniq_ref]
        elevation = get_raster_elev_data(uniq_ref, grid_lats, grid_lons, usgs_db_path)
        elevation_full += elevation
        ts_full += ts

    # reorder the elevation values to match the order of the query coordinates
    ts_full, elevation_full = [
        list(x) for x in zip(*sorted(zip(ts_full, elevation_full), key=lambda pair: pair[0]))
    ]

    return elevation_full


def get_raster_metadata_and_data(raster_path):
    """
    A function that queries the USGS raster database on the Arnaud server
    (/backup/mbap_shared/NED_13/) and returns the elevation values and
    metadata associated with the raster grid at the provided raster path.

    Parameters:
        a file path string to the raster grid file containing elevation values
        of interest
    Returns:
        a tuple containing the following metadata and data
        (Origin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data)
    """
    data_reader = rio.open(raster_path)

    geotransform = data_reader.transform
    xOrigin = geotransform[2]
    yOrigin = geotransform[5]
    pixelWidth = geotransform[0]
    pixelHeight = geotransform[4]
    bands = data_reader.indexes

    return xOrigin, yOrigin, pixelWidth, pixelHeight, bands, data_reader


def get_raster_elev_data(grid_ref, lats, lons, usgs_db_path):
    """
    A function that specifies the path to the raster database, calls
    get_raster_metadata_and_data(raster_path), processes the results
    from raster data into geo-referenced, human-readable, elevation data.

    Parameters:
        a grid reference ID string, an iterable of longitude float values,
        and an iterable of latitude float values
        float value that mark the position of the elevation query
    Returns:
        a list of floats containing elevation values
    """
    elevation = []

    db_path = Path(usgs_db_path)

    raster_path = db_path / f"{grid_ref}" / f"USGS_13_{grid_ref}.tif"

    # if the raster path doesn't get exist, throw an exception
    if not raster_path.exists():
        error_msg = f"The raster path {raster_path} does not exist."
        raise Exception(error_msg)

    (
        xOrigin,
        yOrigin,
        pixelWidth,
        pixelHeight,
        bands,
        data,
    ) = get_raster_metadata_and_data(raster_path)
    xOffset = [int((v - xOrigin) / pixelWidth) if v < 0.0 else "nan" for v in np.float64(lons)]
    yOffset = [int((v - yOrigin) / pixelHeight) if v > 0.0 else "nan" for v in np.float64(lats)]
    band_data = [data.read(b) for b in bands]

    for val in range(len(lons)):
        if xOffset[val] == "nan":
            elevation += [np.nan]
        else:
            for band in band_data:
                try:
                    raster_data = band[yOffset[val], xOffset[val]]
                except IndexError:
                    elevation.append(np.nan)

                elev_ft = float(raster_data) * 3.28084
                elevation.append(elev_ft)

    return elevation


def build_grid_refs(lats, lons):
    """
    This function takes latitude and longitude values and returns
    grid reference IDs that are used as keys for raster grid files

    Parameters:
        Two iterables containing float values. The first containing
        latitudes, and the second containing longitudes.
    Return value:
        A numpy array of grid reference ID strings.
    """
    grid_refs = []
    for i in range(len(lons)):
        if lats[i] > 0.0 and lons[i] < 0.0:
            val = str(int(abs(lons[i])) + 1)
            if len(val) < 3:
                val = "0" + val
            grid_refs += ["n" + str(int(abs(lats[i])) + 1) + "w" + val]
        else:
            grid_refs += ["0"]
    return grid_refs
