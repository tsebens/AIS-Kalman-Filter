import numpy as np

'''
The default functions for estimating 
'''
def default_SoG_estimate(SoG_fact, SoG_meas, SoG_pred):
    SoG_est = (1 - SoG_fact) * SoG_pred + SoG_fact * SoG_meas
    return SoG_est


def defalt_heading_estimate(head_fact, head_meas, head_pred):
    head_est = np.add((1 - head_fact) * head_pred, head_fact * head_meas)
    return head_est


def default_location_estimate(loc_fact, loc_meas, loc_pred):
    loc_est = np.add((1 - loc_fact) * loc_pred, loc_fact * loc_meas)
    return loc_est



# TODO: Instantiate a rule that the SoG can't change by more than n mps in t seconds
# TODO: Instantiate a rule that the heading cannot change by more than n degrees in t seconds
# TODO: Instantiate a rule that the location cannot change by more distance than SoG_est * seconds passed * 1.5 (just to be flexible).
