from random import shuffle

from data_import import order_ais_data_by_ts, pull_data_from_ais_csv, reorder_ais_csv

fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\data\440157000.csv'
reorder_ais_csv(fp)