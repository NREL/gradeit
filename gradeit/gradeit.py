from gradeit.elevation.filtering import elevation_filter
from gradeit.elevation.usgs_local import USGSLocal
from gradeit.elevation.usgs_api import USGSApi
from gradeit.coordinate import Coordinate
from gradeit.grade import get_grade


def gradeit(
    df=None,
    lat_col="lat",
    lon_col="lon",
    filtering=False,
    source="usgs-api",
    usgs_db_path="/backup/mbap_shared/NED_13/",
    des_sg=17,
):
    coordinates = list(
        map(lambda lat, lon: Coordinate.from_lat_lon(lat, lon), zip(df[lat_col], df[lon_col]))
    )

    # Run the appropriate elevation function based on user's desired data source
    if source == "usgs-api":
        emodel = USGSApi()
    elif source == "usgs-local":
        emodel = USGSLocal(usgs_db_path)
    else:
        raise Exception(
            "Invalid elevation data source. Provide one of these options: ['usgs-api','usgs-local']"
        )

    # Get the elevation data
    elevation_ft = emodel.get_elevation(coordinates)
    df["elevation_ft"] = elevation_ft

    # Cases where filtering is desired return both filtered and unfiltered results
    # Select the filtered elevation data for grade derivation
    if filtering:
        elevation_ft_filtered = elevation_filter(
            elevation_profile=elevation_ft, coordinates=coordinates, sg_window=des_sg
        )
        df["elevation_ft_filtered"] = elevation_ft_filtered
        distance_ft_filtered, grade_dec_filtered = get_grade(
            elevation_ft_filtered, coordinates=coordinates
        )
        df["grade_dec_filtered"] = grade_dec_filtered
        df["distance_ft_filtered"] = [0] + list(distance_ft_filtered)
    # Have the unfiltered grade anyways for comparison
    distance_ft_unfiltered, grade_dec_unfiltered = get_grade(elevation_ft, coordinates=coordinates)
    df["distance_ft_unfiltered"] = [0] + list(distance_ft_unfiltered)
    df["grade_dec_unfiltered"] = grade_dec_unfiltered

    return df
