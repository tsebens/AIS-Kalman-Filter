import numpy as np
import matplotlib.pyplot as plot

'''
plt.plot([1,2,3,4], [1,5,10,20], '--^r')
plt.axis([0, 6, 0, 20])
plt.grid()
plt.show()
'''

def plot_points(points, style):
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    print(xs)
    print(ys)
    plot.plot(xs, ys, style)

def plot_data(points):
    style = 'ok-.'
    plot_points(points, style)

def plot_estimates(points):
    style = 'r^-'
    plot_points(points, style)

def plot_predictions(points):
    style = 'bs--'
    plot_points(points, style)

'''
Accepts lists of points data, predictions, and estimates

Each list must be a list of xy tuples.

'''
def make_plot(data, predictions, estimates):
    plot_data(data)
    plot_predictions(predictions)
    plot_estimates(estimates)
    plot.grid()
    plot.legend()
    plot.show()