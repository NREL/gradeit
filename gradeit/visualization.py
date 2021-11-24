import matplotlib.pyplot as plt


def plot_data(df, general_filter, plot_param):
    if plot_param[0]:
        # visualization of elevation data
        if general_filter:
            plt.plot(df['cumulative_uniform_distance_ft'],
                     df['elevation_ft_filtered'],
                     df['cumulative_original_distance_ft'], df['elevation_ft'])
            plt.ylabel('Elevation [ft]')
            plt.xlabel('Distance [ft]')
            plt.grid()
            plt.legend(['filtered', 'unfiltered'])
            plt.title('Elevation vs. Distance')
            plt.show()
        else:
            plt.plot(df['cumulative_original_distance_ft'], df['elevation_ft'])
            plt.ylabel('Elevation [ft]')
            plt.xlabel('Distance [ft]')
            plt.grid()
            plt.title('Elevation vs. Distance')
            plt.show()
    if plot_param[1]:
        # visulalization of grade data
        if general_filter:
            plt.plot(df['cumulative_uniform_distance_ft'],
                     df['grade_dec_filtered'],
                     df['cumulative_original_distance_ft'],
                     df['grade_dec_unfiltered'])
            plt.ylabel('Grade]')
            plt.xlabel('Distance [ft]')
            plt.grid()
            plt.legend(['filtered', 'unfiltered'])
            plt.title('Grade vs. Distance')
            plt.show()
        else:
            plt.plot(df['cumulative_uniform_distance_ft'],
                     df['grade_dec_unfiltered'])
            plt.ylabel('Grade]')
            plt.xlabel('Distance [ft]')
            plt.grid()
            plt.title('Grade vs. Distance')
            plt.show()
    if not plot_param[0] and not plot_param[0]:
        print('No visualization selected.')