import numpy as np

from convert import knts_to_mps

'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME FUNCTION SIGNATURE
All functions should have a uniform function signature, where all parameters have the same name, and the same order
In addition, all parameters should be given empty default values. This way, any function that is called will simply 
have the relevant parameters overridden

Because of this, whenever the functions are called, the parameters must be explicitly named
'''


'''
The default prediction functions
'''
def default_SoG_prediction(loc_est=None, head_est=None, SoG_est=None, curr_state=None, prev_state=None):
    if prev_state==None:
        SoG_pred = SoG_est  # We assume that vessels maintain their speed over time.
    else:
        SoG_pred = prev_state.SoG_state.est # We assume that vessels maintain their speed over time.
    return SoG_pred


def default_heading_prediction(loc_est=None, head_est=None, SoG_est=None, curr_state=None, prev_state=None):
    if prev_state==None:
        head_pred = head_est  # We assume that vessels maintain their heading over time.
    else:
        head_pred = prev_state.head_state.est
    return head_pred


def default_location_prediction(loc_est=None, head_est=None, SoG_est=None, curr_state=None, prev_state=None):
    if prev_state==None:
        loc_pred = np.add(loc_est, head_est * SoG_est)
    else:
        loc_pred = np.add(prev_state.loc_state.est, prev_state.head_state.est * prev_state.SoG_state.est)
    return loc_pred



'''
Custom behaviour prediction functions
'''
# Enforces a strict rule that the estimated SoG of the vessel cannot exceed max_spd knots
def SoG_prediction_max_spd(loc_est=None, head_est=None, SoG_est=None, max_spd=15):
    return SoG_est if SoG_est < knts_to_mps(max_spd) else knts_to_mps(max_spd)



