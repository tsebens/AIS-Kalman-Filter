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
def default_SoG_prediction(curr_state, prev_state):
    return prev_state.SoG_state.est # We assume that vessels maintain their speed over time.



def default_heading_prediction(curr_state, prev_state):
    return prev_state.head_state.est



def default_location_prediction(curr_state, prev_state):
    return np.add(prev_state.loc_state.est, prev_state.head_state.est * prev_state.SoG_state.est)




'''
Custom behaviour prediction functions
'''
# Enforces a strict rule that the estimated SoG of the vessel cannot exceed max_spd knots
def SoG_prediction_max_spd(loc_est=None, head_est=None, SoG_est=None, max_spd=15):
    return SoG_est if SoG_est < knts_to_mps(max_spd) else knts_to_mps(max_spd)



