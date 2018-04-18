'''
Collection of value objects meant to provide some structure to the values used in the filter.
'''
# Value object that holds the state of a particular vessel variable (location, heading, speed over ground)
from collections import OrderedDict


class VarState:
    def __init__(self, meas=None, pred=None, est=None):
        self.meas = meas
        self.pred = pred
        self.est  = est


# Value object that holds the state of a particular vessel.
class VesselState:
    def __init__(self, loc_state=None, head_state=None, SoG_state=None, timestamp=None, row: OrderedDict=None):
        self.loc_state = loc_state
        self.head_state = head_state
        self.SoG_state = SoG_state
        self.timestamp = timestamp
        self.row=row


# Value object to hold the various factors used during the filter's processing
class FactorState:
    def __init__(self, loc_fact:float=1.0, head_fact:float=1.0, SoG_fact:float=1.0):
        self.location_factor = loc_fact
        self.heading_factor = head_fact
        self.SoG_factor = SoG_fact


# Define the prediction and estimation functions for a given variable
class FunctionState:
    def __init__(self, predict, estimate):
        self.predict = predict
        self.estimate = estimate


# Value object that holds the configuration value for an instance of the Kalman filter
# Holds things like the functions to make estimates and predictions, any unique constant
# values (loc_fact, head_fact, etc..), as well as anything else the filter might need.
class FilterState:
    def __init__(self, factor_state: FactorState,
                 loc_function_state: FunctionState,
                 head_function_state: FunctionState,
                 SoG_function_state: FunctionState):
        self.factors = factor_state
        self.location_functions = loc_function_state
        self.heading_functions = head_function_state
        self.SoG_functions = SoG_function_state
