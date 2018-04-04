import numpy as np

from calculate import angle_between, rotate_vector, vector_between_two_points, vector_length
from configuration import MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND, MAX_ALLOWABLE_VESSEL_ACCELERATION_KNTS_PER_SECOND
from convert import make_est_from_meas_pred_and_fact, seconds_passed
from state import VesselState, FilterState

'''
The estimation step is where we combine what we predicted about the state of the vessel with what we measured, and do so 
in an intelligent and intentional manner.
'''


'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME DEFAULT FUNCTION SIGNATURE
Additional named variables are okay as long as they have default values
All functions should have a uniform function signature, where all parameters have the same name, and the same order
In addition, all parameters should be given empty default values. This way, any function that is called will simply 
have the relevant parameters overridden
'''

'''
The default functions for estimating 
'''
def default_SoG_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    SoG_fact = filter_state.factors.SoG_factor
    return make_est_from_meas_pred_and_fact(curr_state.SoG_state.meas,
                                            curr_state.SoG_state.pred,
                                            SoG_fact)


def default_heading_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    head_fact = filter_state.factors.heading_factor
    return make_est_from_meas_pred_and_fact(curr_state.head_state.meas,
                                            curr_state.head_state.pred,
                                            head_fact)


def default_location_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    loc_fact = filter_state.factors.location_factor
    return make_est_from_meas_pred_and_fact(curr_state.loc_state.meas,
                                            curr_state.loc_state.pred,
                                            loc_fact)


# Returns the SoG estimate, but caps the estimate under the rule that the vessel cannot gain more than
# max_acc knts per second of acceleration. It is assumed that a boat can lose speed as quickly as it likes.
def est_SoG_max_spd(filter_state:FilterState, curr_state:VesselState, prev_state:VesselState, max_acc=MAX_ALLOWABLE_VESSEL_ACCELERATION_KNTS_PER_SECOND):
    SoG_fact = filter_state.factors.SoG_factor
    time_passed = curr_state.timestamp - prev_state.timestamp
    max_spd_change = max_acc * time_passed.total_seconds()

    return min(
        default_SoG_estimate(filter_state, curr_state, prev_state),
        prev_state.SoG_state.est + max_spd_change
    )


# Estimate the new heading based on the prediction, and the measurement, but with the rule that the
# heading can only change so fast.
def est_head_max_turn(filter_state:FilterState, curr_state:VesselState, prev_state:VesselState, max_turn=MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND):
    total_seconds = seconds_passed(curr_state, prev_state)
    max_head_change = max_turn * total_seconds
    # First we make our usual estimate, then we compare that to our rules.
    pred_heading = default_heading_estimate(filter_state, curr_state, prev_state)
    # If the predicted heading would exceed the allowable heading change,
    # then use the max heading change value instead
    if angle_between(prev_state.head_state.est, pred_heading) > max_head_change:
        # This next part is actually sort of a work around. I don't know mathematically how to
        # derive the heading unit vector, because there are two possible values. I calculate
        # them both here, then determine which one is the better answer.
        v1 = rotate_vector(prev_state.head_state.est, max_head_change)
        v2 = rotate_vector(prev_state.head_state.est, -1 * max_head_change)
        if angle_between(v1, pred_heading) < angle_between(v2, pred_heading):
            # v1 is closer to the predicted heading than v1, which means its the appropriate estimation
            return v1
        else:
            return v2
    else:
        # If we reach this point, then the predicted heading is within allowable tolerances.
        return pred_heading

# TODO: Instantiate a rule that the location cannot change by more distance than SoG_est * seconds passed * 1.5 (just to be flexible).'
def est_loc_max_dis(filter_state:FilterState, curr_state:VesselState, prev_state:VesselState):
    # First we get our default estimation, then we compare that to our rules
    est_location = default_location_estimate(filter_state, curr_state, prev_state)
    # Now we get the vector between our new estimate and our estimated location from the previous state
    delta_v = vector_between_two_points(prev_state.loc_state.est, est_location)
    # The length of delta_v represents the distance we travelled
    distance = vector_length(delta_v)
    # This is the crux of it. If this distance is too large, then we have to intervene.
    # First we calculate our max allowable distance
    total_seconds = seconds_passed(curr_state, prev_state)
    max_allowable_distance = prev_state.SoG_state.est * total_seconds


