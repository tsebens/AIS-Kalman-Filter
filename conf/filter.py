from estimation import est_loc_max_dis, est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, default_location_estimate, \
    default_SoG_estimate
from prediction import default_location_prediction, default_heading_prediction, default_SoG_prediction
from state import FactorState, FunctionState, FilterState
"""
--------------------------------------------------------------------------------------------
Filter configuration
--------------------------------------------------------------------------------------------
"""

"""These factors dictate the ratio at which the prediction and the measurement will be mixed to produce the estimate"""
"""A higher factor means that the measurement will be favored. A lower fact means that the prediction will be favored"""
factor_state = FactorState(
    loc_fact=0.2,
    head_fact=0.2,
    SoG_fact=0.8
)
"""These function states define the functions that will be used for the prediction and estimation steps of the filter."""
location_functions = FunctionState(
    predict=default_location_prediction,
    estimate=default_location_estimate
)
heading_functions = FunctionState(
    predict=default_heading_prediction,
    estimate=est_head_max_turn_per_sec
)
SoG_functions = FunctionState(
    predict=default_SoG_prediction,
    estimate=est_SoG_max_spd_per_sec
)
"""This is essentially just a box to put all of the above values in."""
filter_state = FilterState(
    factor_state,
    location_functions,
    heading_functions,
    SoG_functions
)