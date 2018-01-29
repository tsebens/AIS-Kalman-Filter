import plotter
import h_g_filter
import data_gen
import math

loc_fact = .25
head_fact = .25
SoG_fact = .25

def sin_1_4th(x):
    return math.sin(x/4)

data = list(data_gen.gen_data(sin_1_4th, .6, 100))

estimates, loc_pred, head_pred, sog_pred = h_g_filter.ais_kalman(data, loc_fact, head_fact, SoG_fact)
plotter.make_plot(data, loc_pred, estimates)