# Kalman filter
from calculate import distance_between_two_points
from convert import make_initial_filter_state, seconds_passed_between_states
from state import FilterState, VesselState
from conf.static import MAX_ALLOWABLE_VESSEL_SPEED


"""
Executes a Kalman filter on the passed ais_data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in ais_data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.

The filter_state is a value object which contains a lot of information about the way in which the filter should behave
Refer to the FilterState object documentation for a more complete description.
"""


def ais_kalman(vessel_states, filter_state: FilterState):
    # Populate our initial values
    prev_state = make_initial_filter_state(vessel_states.__next__())
    filtered_states = [prev_state,]
    # Now, for every data point we have (skipping the first one since we've already loaded those values) we use the
    # Kalman filter to estimate the true location of our vessel.
    for curr_state in vessel_states:
        # Now we can make our predictions for location, heading, and SoG
        predict_step(curr_state, prev_state, filter_state)
        # Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
        estimate_step(curr_state, prev_state, filter_state)
        # If the point is outside of the bounds we set, flag it.
        curr_state = flag_state(curr_state, prev_state)
        # Record the current state of the vessel.
        filtered_states.append(curr_state)
        # If the current point is flagged, then we don't want to reference it when we consider the next point, so we'll skip this part
        if not curr_state.is_flagged:
            # Reset the state variable for the next iteration
            prev_state = curr_state
            
    return filtered_states


def estimate_step(curr_state: VesselState, prev_state: VesselState, filter_state: FilterState):
    curr_state.head_state.est = \
        filter_state.heading_functions.estimate(filter_state, curr_state, prev_state)
    curr_state.SoG_state.est = \
        filter_state.SoG_functions.estimate(filter_state, curr_state, prev_state)
    curr_state.loc_state.est = \
        filter_state.location_functions.estimate(filter_state, curr_state, prev_state)


def predict_step(curr_state: VesselState, prev_state: VesselState, filter_state: FilterState):
    curr_state.head_state.pred = \
        filter_state.heading_functions.predict(curr_state, prev_state)
    curr_state.SoG_state.pred = \
        filter_state.SoG_functions.predict(curr_state, prev_state)
    curr_state.loc_state.pred = \
        filter_state.location_functions.predict(curr_state, prev_state)


def flag_state(curr_state, prev_state):
    distance = distance_between_two_points(prev_state.loc_state.est,
                                curr_state.loc_state.meas)
    time_passed = seconds_passed_between_states(curr_state, prev_state)
    required_speed = distance / time_passed
    if required_speed > 1.5 * MAX_ALLOWABLE_VESSEL_SPEED:    
        curr_state.is_flagged = True
    return curr_state


