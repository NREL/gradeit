from typing import List

import numpy as np
from scipy import signal

from gradeit.coordinate import Coordinate
from gradeit.grade import get_distances


def elevation_filter(
    elevation_profile=List[float], coordinates=List[Coordinate], sg_window: int = 17
) -> List[float]:
    """
    This implementation applies the SG filter in the temporal domain
    as opposed to the spatial domain. Filtering spatially requires
    error-proned resampling of the elevation signal to match a uniform
    distance between each point.

    Parameters:
        elevation_profile: a list of elevation values
        coordinates: a list of Coordinate objects
        sg_window: the Savitzky-Golay filter window size

    Returns:
        a list of filtered elevation values
    """

    distances = get_distances(coordinates)
    cuml_dist = list(np.append(0, np.cumsum(distances)))

    # note: run final check on user SG value, provide default value if necessary
    sg_window = check_sg(sg_window, cuml_dist)

    # run SavGol filter
    elev_linear_sg = signal.savgol_filter(elevation_profile, window_length=sg_window, polyorder=3)

    return elev_linear_sg


def check_sg(sg_window: int, cumlDist: List[float]) -> int:
    # compute the default value of SG window.
    avg_spd = cumlDist[-1] / len(cumlDist)  # vehicle avg speed in ft/s
    filter_width = 2500  # in [ft], width of the spike to be filtered (tentative)
    filter_factor = 5
    polyorder = 3  # fixed value, do not change!
    df_filter = round(
        filter_width / avg_spd * filter_factor
    )  # (estimated formula, change filter_width and filter_factor to get desired effect)
    if df_filter < polyorder:
        df_filter = polyorder + 2
    elif df_filter > len(cumlDist):
        df_filter = int(round(len(cumlDist) * 0.75))  # safeguard against crossing sg array size
    sg_default = df_filter
    if sg_default % 2 == 0:
        sg_default += 1  # if even, transform to odd

    # user inputs 0 to access the default value (see basic.py)
    if sg_window == 0:
        return sg_default
    else:
        # checks the validility of the user defined window
        if sg_window % 2 == 0:
            sg_window += 1
        if (sg_window > len(cumlDist)) or (
            sg_window < 3
        ):  # sg_window must be greater than polyorder = 3 and less than df size
            sg_window = sg_default
        return sg_window
