import numpy as np
import matplotlib.pyplot as plot

'''
plt.plot([1,2,3,4], [1,5,10,20], '--^r')
plt.axis([0, 6, 0, 20])
plt.grid()
plt.show()
'''

def show_plot():
    plot.show()


def plot_points(points, style):
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    plot.plot(xs, ys, style)

# Plots the input points in the format of location data
def plot_loc_data(points):
    style = 'ok-.'
    plot_points(points, style)

# Plots the input points in the format of the location estimates
def plot_loc_estimates(points):
    style = 'r^-'
    plot_points(points, style)

# Plots the input points in the format of the location predictions
def plot_loc_predictions(points):
    style = 'bs--'
    plot_points(points, style)


def plot_b_func(points):
    style = 'g--'
    plot_points(points, style)

'''
Accepts lists of points loc_data, predictions, and estimates

Each list must be a list of xy tuples.

'''
def make_plot(loc_data, loc_preds, loc_ests):
    plot_loc_data(loc_data)
    plot_loc_predictions(loc_preds)
    plot_loc_estimates(loc_ests)

'''
Same as make_plot, but it plots the point in a step by step manner

If b_func is defined, the system will plot the base function as a green dotted line behind the other plots.
'''
def make_iterative_plot(loc_data, loc_preds, loc_ests, b_func=None, delay=0.5):
    plot.grid()
    if b_func != None:
        b_vals = [(point[0], b_func(point[0])) for point in loc_data]
    for i in range(len(loc_data)-1):
        curr_loc_data = loc_data[:i]
        curr_loc_preds = loc_preds[:i]
        curr_loc_ests = loc_ests[:i]
        if b_func != None:
            curr_b_vals = b_vals[:i]
            plot_b_func(curr_b_vals)
        make_plot(curr_loc_data, curr_loc_preds, curr_loc_ests)

        plot.pause(delay)

def make_comparison_plot(loc_data, loc_estimates, loc_predictions, head_data, head_estimates, head_predicitions, func):
    plot.grid()
    plot_loc_data(loc_data)
    plot_loc_estimates(loc_estimates)
    plot_loc_predictions(loc_predictions)
    plot_heading_data(head_data, loc_data)
    plot_heading_estimates(head_estimates, loc_estimates)
    plot_heading_predictions(head_predicitions, loc_predictions)

    plot_points([(point[0], func(point[0])) for point in loc_data], 'g--') # Plot the actual function without noise
    plot.show()


def plot_heading_predictions(head_pred, loc_pred):
    plot.axes().quiver([point[0] for point in loc_pred], [point[1] for point in loc_pred],
                       [point[0] for point in head_pred], [point[1] for point in head_pred],
                       color=['b' for point in head_pred],
                       width=0.001,
                       )


def plot_heading_data(head_data, loc_data):
    plot.axes().quiver([point[0] for point in loc_data], [point[1] for point in loc_data],
                       [point[0] for point in head_data], [point[1] for point in head_data],
                       color=['k' for point in head_data],
                       width=0.001,
                       )


def plot_heading_estimates(head_estimates, loc_estimates):
    plot.axes().quiver([point[0] for point in loc_estimates], [point[1] for point in loc_estimates],
                       [point[0] for point in head_estimates], [point[1] for point in head_estimates],
                       color=['r' for point in head_estimates],
                       width=0.001
                       )

def plotEstimatedValues(ax, head_est, loc_est, delay):
    ax.arrow(loc_est[0], loc_est[1], head_est[0], head_est[1], head_width=0.05, head_length=0.1, fc='r', ec='r')
    plot.scatter(loc_est[0], loc_est[1], c='r')
    plot.pause(delay)

def plotPredictedValues(ax, head_pred, loc_pred, delay):
    plot.scatter(loc_pred[0], loc_pred[1], c='b')
    ax.arrow(loc_pred[0], loc_pred[1], head_pred[0], head_pred[1], head_width=0.05, head_length=0.1, fc='b', ec='b')
    plot.pause(delay)

def plotMeasuredValues(ax, head_meas, loc_meas, delay):
    ax.arrow(loc_meas[0], loc_meas[1], head_meas[0], head_meas[1], head_width=0.05, head_length=0.1, fc='k', ec='k')
    plot.scatter(loc_meas[0], loc_meas[1], c='k')
    plot.pause(delay)