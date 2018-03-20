from data_import import pull_data_from_ais_csv, convert_ais_data_to_usable_form
from plot import plot_loc_data, show_plot

fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\data\367186180.csv'
# raw_ais = pull_data_from_ais_csv(fp)
parsed_ais = list(convert_ais_data_to_usable_form(fp))
plot_loc_data([point[0] for point in parsed_ais])
print(len(parsed_ais))
show_plot()
