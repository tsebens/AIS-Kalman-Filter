from data import gen_random_data, sin_1_4th
from h_g_filter import ais_kalman
from plot import make_iterative_plot

loc_fact = 0.2
head_fact = 0.4
SoG_fact =0.4


data = gen_random_data()
loc_data = [row[0] for row in data]
head_data = [row[1] for row in data]
sog_data = [row[2] for row in data]
loc_estimates, loc_predictions, head_estimates, head_predictions, SoG_estimates, SoG_predictions = ais_kalman(data, loc_fact, head_fact, SoG_fact)
make_iterative_plot(loc_data, loc_predictions, loc_estimates, b_func=sin_1_4th)