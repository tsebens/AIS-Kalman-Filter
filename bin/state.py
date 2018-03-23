'''
Collection of value objects meant to provide some structure to the values used in the filter.
'''


# Value object that holds the state of a particular vessel variable (location, heading, speed over ground)
class VarState:
    meas = None
    pred = None
    est  = None

    def __init__(self, meas=None, pred=None, est=None):
        self.meas = meas
        self.pred = pred
        self.est  = est


# Value object that holds the state of a particular vessel.
class VesselState:
    loc_state = None
    head_state = None
    SoG_state = None
    timestamp = None

    def __init__(self, loc_state=None, head_state=None, SoG_state=None, timestamp=None):
        self.loc_state = loc_state
        self.head_state = head_state
        self.SoG_state = SoG_state
        self.timestamp = timestamp

