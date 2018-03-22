import numpy as np
'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME FUNCTION SIGNATURE
'''

def default_SoG_prediction(SoG_est):
    SoG_pred = SoG_est  # We assume that vessels maintain their speed over time.
    return SoG_pred


def default_heading_prediction(head_est):
    head_pred = head_est  # We assume that vessels maintain their heading over time.
    return head_pred


def default_location_prediction(SoG_est, head_est, loc_est):
    loc_pred = np.add(loc_est, head_est * SoG_est)
    return loc_pred