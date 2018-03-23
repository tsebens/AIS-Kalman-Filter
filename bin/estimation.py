import numpy as np

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



# TODO: Instantiate a rule that the SoG can't change by more than n knts in t seconds
# Returns the SoG estimate, but caps the estimate under the rule that the vessel cannot gain more than
# max_acc knts per second of acceleration. It is assumed that a boat can lose speed as quickly as it likes.
def est_SoG_max_spd(SoG_fact, curr_state, prev_state, max_acc=0.5):
    time_passed = curr_state.timestamp - prev_state.timestamp
    seconds_passed = time_passed.seconds_passed
    max_spd_change = max_acc * seconds_passed
    SoG_est = (1-SoG_fact) * curr_state.SoG_state.pred + curr_state.SoG_state.meas * SoG_fact
    if SoG_est > prev_state.SoG_state.est + max_spd_change:
        SoG_est = prev_state.SoG_state.est + max_spd_change
    return SoG_est

# TODO: Instantiate a rule that the heading cannot change by more than n degrees in t seconds
# TODO: Instantiate a rule that the location cannot change by more distance than SoG_est * seconds passed * 1.5 (just to be flexible).
