# Kalman filter
from convert import make_initial_state, make_state_from_deprecated_ais_data_format as make_state
from estimation import default_SoG_estimate, defalt_heading_estimate, default_location_estimate
from prediction import default_SoG_prediction, default_heading_prediction, default_location_prediction

'''
Executes a Kalman filter on the passed ais_data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in ais_data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.
Data is an nx4 numpy array, each row of which == (loc, heading, SoG, time)
loc must be a numpy array, representing Lat/Lon (lat, lon)
Heading must be a unit vector (length 1), and must come in as a numpy array (lat, lon)
SoG must be in DecDeg/sec
time must be an aware datetime object (timezone aware)
loc_, head_, and SoG_ fact's' represent the consideration factors for each value. Essentially a measure of the proportion 
of the final estimate that will be made up of the measurement. 
A high fact will result in a higly influential measurement: 
the final estimates will be very faithful to the measurements. 
A low fact will result in a very uninfluential measurement: 
the final estimates will be far more closely tied to the predictions made prior to the estimates.

In simpler terms, think of fact as a metric of how trustworthy a set of measurements are: A low fact is good for 
measurements that are error prone. A high fact is good for measurements that tend to be accurate.

The prediction and estimation functions are used to provide the predictions and the estimates for the new values 
of the location, heading, and speed, based on the relevant previous values.
By defining these as passed functions with default values, it becomes possible to inject the logi which 
the filter uses to make it's predictions and estimates.
'''
def ais_kalman(data, filter_state):
    pred_location, pred_heading, pred_SoG = init_prediction_functions(filter_state)
    est_location, est_heading, est_SoG = init_estimation_function(filter_state)
    # Initialize our lists for storing the results of the filter
    loc_predictions, head_predictions, SoG_predictions, loc_estimates, head_estimates, SoG_estimates = [], [], [], [], [], []
    vessel_states = []
    # Populate our initial values
    prev_state = make_initial_state(data[0])
    # Now, for every data point we have (skipping the first one since we've already loaded those values) we use the
    # Kalman filter to estimate the true location of our vessel.
    for curr_state in data[1:]:
        # Now we can make our predictions for location, heading, and SoG
        prediction_step(curr_state, filter_state, prev_state)
        # Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
        estimate_step(curr_state, filter_state, prev_state)
        # Record the previous state of the vessel.
        vessel_states.append(prev_state)
        # Reset the state variable for the next iteration
        prev_state = curr_state
    return vessel_states


def estimate_step(curr_state, filter_state, prev_state):
    curr_state.loc_state.est = filter_state.location_functions.estimate(
        filter_state.factors.location_factor, curr_state, prev_state)
    curr_state.head_state.est = filter_state.heading_functions.estimate(
        filter_state.factors.heading_factor, curr_state, prev_state)
    curr_state.SoG_state.est = filter_state.SoG_functions.estimate(
        filter_state.factors.SoG_factor, curr_state, prev_state)


def prediction_step(curr_state, filter_state, prev_state):
    curr_state.loc_state.pred = filter_state.location_functions.predict(
        curr_state, prev_state)
    curr_state.head_state.pred = filter_state.heading_functions.predict(
        curr_state, prev_state)
    curr_state.SoG_state.pred = filter_state.SoG_functions.predict(
        curr_state, prev_state)


def init_prediction_functions(filter_state):
    l_p = filter_state.location_functions.predict
    h_p = filter_state.heading_functions.predict
    s_p = filter_state.SoG_functions.predict
    return l_p, h_p, s_p


def init_estimation_function(filter_state):
    l_e = filter_state.location_functions.estimate
    h_e = filter_state.heading_functions.estimate
    s_e = filter_state.SoG_functions.estimate
    return l_e, h_e, s_e

