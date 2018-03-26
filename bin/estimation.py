import numpy as np

from calculate import angle_between, rotate_vector
from convert import make_est_from_meas_pred_and_fact
from state import VesselState

'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME FUNCTION SIGNATURE
All functions should have a uniform function signature, where all parameters have the same name, and the same order
In addition, all parameters should be given empty default values. This way, any function that is called will simply 
have the relevant parameters overridden
'''

'''
The default functions for estimating 
'''
def default_SoG_estimate(SoG_fact=None, curr_state=None, prev_state=None):
    return (1 - SoG_fact) * curr_state.SoG_state.pred + SoG_fact * curr_state.SoG_state.meas


def defalt_heading_estimate(head_fact=None, curr_state=None, prev_state=None):
    return np.add((1 - head_fact) * curr_state.head_state.pred, head_fact * curr_state.head_state.meas)


def default_location_estimate(loc_fact=None, curr_state=None, prev_state=None):
    return np.add((1 - loc_fact) * curr_state.loc_state.pred, loc_fact * curr_state.loc_state.meas)



# Returns the SoG estimate, but caps the estimate under the rule that the vessel cannot gain more than
# max_acc knts per second of acceleration. It is assumed that a boat can lose speed as quickly as it likes.
def est_SoG_max_spd(SoG_fact, curr_state, prev_state, max_acc=0.5):
    time_passed = curr_state.timestamp - prev_state.timestamp
    max_spd_change = max_acc * time_passed.seconds_passed

    return min(
        make_est_from_meas_pred_and_fact(curr_state.SoG_state.meas, curr_state.SoG_state.pred, SoG_fact),
        prev_state.SoG_state.est + max_spd_change
    )

# Returns the heading estimate, but caps the estimate under the rule that the vessel cannot turn more than
# max_turn degrees per second.
def est_head_max_turn(head_fact, curr_state: VesselState, prev_state: VesselState, max_turn=5):
    time_passed = curr_state.timestamp - prev_state.timestamp
    max_head_change = max_turn * time_passed.seconds_passed
    pred_heading = make_est_from_meas_pred_and_fact(curr_state.head_state.meas,
                                                    curr_state.head_state.pred,
                                                    head_fact)

    if angle_between(prev_state.head_state.est, pred_heading) > max_head_change:
        # If the predicted heading would exceed the allowable heading change,
        # then use the max heading change value instead
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




# TODO: Instantiate a rule that the location cannot change by more distance than SoG_est * seconds passed * 1.5 (just to be flexible).
