import numpy as np

from configuration import MAX_ALLOWABLE_VESSEL_SPEED
from convert import knts_to_mps, seconds_passed_between_states

'''
The prediction step is where you predict what the state of the vessel WILL BE, based on what you know about the boat in 
it's previous state. In other words:

WHAT DO YOU KNOW ABOUT BOATS AND HOW THEY TYPICALLY BEHAVE AND, BASED ON THAT, HOW DO YOU EXPECT THIS BOAT TO BEHAVE?
'''

'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME FUNCTION SIGNATURE
All functions should have a uniform function signature, because they are meant to be easily interchangable
Because of this, whenever the functions are called, the parameters must be explicitly named
'''


'''
The default prediction functions
'''
def default_SoG_prediction(curr_state, prev_state):
    return prev_state.SoG_state.est # We assume that vessels maintain their speed over time.


def default_heading_prediction(curr_state, prev_state):
    return prev_state.head_state.est # We assume that vessels maintain their heading over time.


def default_location_prediction(curr_state, prev_state):
    # We assume that a vessels location is a direct and exact product of it's previous location, heading, and speed.
    t = seconds_passed_between_states(curr_state, prev_state)
    return np.add(prev_state.loc_state.est, prev_state.head_state.est * prev_state.SoG_state.est * t)





