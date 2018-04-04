# Kalman filter
from convert import make_initial_state
from state import FilterState

'''
Executes a Kalman filter on the passed ais_data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in ais_data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.

The filter_state is a value object which contains a lot of information about the way in which the filter should behave
Refer to the FilterState object documentation for a more complete description.
'''
def ais_kalman(data, filter_state: FilterState):
    vessel_states = []
    # Populate our initial values
    prev_state = make_initial_state(data[0])
    # Now, for every data point we have (skipping the first one since we've already loaded those values) we use the
    # Kalman filter to estimate the true location of our vessel.
    for curr_state in data[1:]:
        # Now we can make our predictions for location, heading, and SoG
        prediction_step(curr_state, prev_state, filter_state)
        # Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
        estimate_step(curr_state, prev_state, filter_state)
        # Record the previous state of the vessel.
        vessel_states.append(prev_state)
        # Reset the state variable for the next iteration
        prev_state = curr_state
    return vessel_states


def estimate_step(curr_state, prev_state, filter_state):
    curr_state.head_state.est = filter_state.heading_functions.estimate(
        filter_state, curr_state, prev_state)
    curr_state.SoG_state.est = filter_state.SoG_functions.estimate(
        filter_state, curr_state, prev_state)
    curr_state.loc_state.est = filter_state.location_functions.estimate(
        filter_state, curr_state, prev_state)

def prediction_step(curr_state, prev_state, filter_state):
    curr_state.loc_state.pred = filter_state.location_functions.predict(
        curr_state, prev_state)
    curr_state.head_state.pred = filter_state.heading_functions.predict(
        curr_state, prev_state)
    curr_state.SoG_state.pred = filter_state.SoG_functions.predict(
        curr_state, prev_state)
