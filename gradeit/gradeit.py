from gradeit import elevation, grade


def gradeit(
    df=None,
    lat_col="lat",
    lon_col="lon",
    filtering=False,
    source="usgs-api",
    usgs_db_path="/backup/mbap_shared/NED_13/",
    des_sg=17,
):
    coordinates = list(zip(df[lat_col], df[lon_col]))

    # Run the appropriate elevation function based on user's desired data source
    if source == "usgs-api":
        df = elevation.usgs_api(
            df,
            lat=lat_col,
            lon=lon_col,
            apply_filter=filtering,
            sg_window=des_sg,
        )

    elif source == "usgs-local":
        df = elevation.usgs_local_data(
            df,
            usgs_db_path=usgs_db_path,
            lat=lat_col,
            lon=lon_col,
            filter=filtering,
            sg_window=des_sg,
        )

    else:
        raise Exception(
            "Invalid elevation data source. Provide one of these options: ['usgs-api','usgs-local']"
        )

    # Cases where filtering is desired return both filtered and unfiltered results
    # Select the filtered elevation data for grade derivation
    if filtering:
        elev_arr_filtered = df["elevation_ft_filtered"].values
        distance_ft_filtered, grade_dec_filtered = grade.get_grade(
            elev_arr_filtered, coordinates=coordinates
        )
        df["grade_dec_filtered"] = grade_dec_filtered
        df["distance_ft_filtered"] = [0] + list(distance_ft_filtered)
    # Have the unfiltered grade anyways for comparison
    elev_arr_unfiltered = df["elevation_ft"].values
    distance_ft_unfiltered, grade_dec_unfiltered = grade.get_grade(
        elev_arr_unfiltered, coordinates=coordinates
    )
    df["distance_ft_unfiltered"] = [0] + list(distance_ft_unfiltered)
    df["grade_dec_unfiltered"] = grade_dec_unfiltered

    # df['cumulative_distance_ft'] = np.cumsum(df['distance_ft']) #added: 06/15

    return df
