from data import gen_random_data
from plot import make_iterative_plot

fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\data\367186180.csv'
data = gen_random_data()
loc_data = [row[0] for row in data]
head_data = [row[1] for row in data]
sog_data = [row[2] for row in data]
make_iterative_plot(loc_data, head_data, sog_data, 0.5)