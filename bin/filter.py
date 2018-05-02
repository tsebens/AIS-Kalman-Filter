# Kalman filter
from calculate import distance_between_two_points
from convert import make_initial_filter_state, seconds_passed_between_states, mps_to_knts
from state import FilterState, VesselState

"""
Executes a Kalman filter on the passed ais_data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in ais_data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.

The filter_state is a value object which contains a lot of information about the way in which the filter should behave
Refer to the FilterState object documentation for a more complete description.
"""
def ais_kalman(vessel_states, filter_state: FilterState):
    filtered_states = []
    # Populate our initial values
    prev_state = make_initial_filter_state(vessel_states.__next__())
    # Now, for every data point we have (skipping the first one since we've already loaded those values) we use the
    # Kalman filter to estimate the true location of our vessel.
    count = 0
    for curr_state in vessel_states:
        # Now we can make our predictions for location, heading, and SoG
        prediction_step(curr_state, prev_state, filter_state)
        # Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
        estimate_step(curr_state, prev_state, filter_state)
        # Record the previous state of the vessel.
        filtered_states.append(prev_state)
        # yield prev_state # todo: Implement this later. Make the filter into a generator, rather than a list-to-list conversion
        # Reset the state variable for the next iteration
        distance = distance_between_two_points(curr_state.loc_state.meas, prev_state.loc_state.meas)
        time = seconds_passed_between_states(curr_state, prev_state)
        speed = distance/time
        print('---------------')
        print('%s' % count)
        print('Speed derived from measured values: %s m/s  --  %s knts' % (speed, mps_to_knts(speed)))
        print('Speed according to vessel state:    %s m/s  --  %s knts' % (curr_state.SoG_state.meas, mps_to_knts(curr_state.SoG_state.meas)))
        print('Estimated vessel speed:             %s m/s  --  %s knts' % (curr_state.SoG_state.est, mps_to_knts(curr_state.SoG_state.est)))
        prev_state = curr_state
        count += 1
    return filtered_states


def estimate_step(curr_state: VesselState, prev_state: VesselState, filter_state: FilterState):
    curr_state.head_state.est = \
        filter_state.heading_functions.estimate(filter_state, curr_state, prev_state)
    curr_state.SoG_state.est = \
        filter_state.SoG_functions.estimate(filter_state, curr_state, prev_state)
    curr_state.loc_state.est = \
        filter_state.location_functions.estimate(filter_state, curr_state, prev_state)


def prediction_step(curr_state: VesselState, prev_state: VesselState, filter_state: FilterState):
    curr_state.head_state.pred = \
        filter_state.heading_functions.predict(curr_state, prev_state)
    curr_state.SoG_state.pred = \
        filter_state.SoG_functions.predict(curr_state, prev_state)
    curr_state.loc_state.pred = \
        filter_state.location_functions.predict(curr_state, prev_state)
