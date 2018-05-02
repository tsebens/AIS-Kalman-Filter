# Logic class for any conversions that need to be made
from math import tan, radians
import numpy as np
from datetime import datetime

from conf.static import knts_to_mps_conv_fact
from state import VarState, VesselState
from timezones import UTC


# Converts a true heading to a unit vector
def true_heading_to_unit_vector(heading):
    unit_v = np.array([1, tan(radians(heading))])
    mag = np.linalg.norm(unit_v)
    unit_v = unit_v/mag
    unit_v = np.array([unit_v[1], unit_v[0]])
    return unit_v


def unit_vectorto_true_heading(vector):
    # TODO: Implement this function
    raise Exception('You still have to implement this conversion function, shithead.')


# Convert an ais format timestamp to a datetime object.
def ais_timestamp_to_datetime(timestamp, tz=UTC):
    date, time = timestamp.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), second=int(second), tzinfo=tz)


# Convert a lat/lon pair to a vector
def lat_lon_to_loc_vector(point, lat_fn='AA_LAT', lon_fn='AA_LON'):
    aa_lat = point[lat_fn]
    aa_lon = point[lon_fn]
    return np.array([aa_lat, aa_lon])


# Convert knots to meters per second
def knts_to_mps(knts):
    return knts * knts_to_mps_conv_fact

def mps_to_knts(mps):
    return mps / knts_to_mps_conv_fact


# Makes a state in which for all VarStates, the estimated and predicted values are the same as the measured values
# Essentially make a state in which we must assume that the measured values are 100% accurate.
def make_initial_state_from_deprecated_ais_data_format(data):
    state = make_state_from_deprecated_ais_data_format(data)
    make_initial_filter_state(state)
    return state


# When the filter starts, it cannot make an estimate for the current point unless there is a previous point with
# estimates we can compare it to. To get around this, we simply assume that the first state we see is perfectly
# accurate in it's measurements, and set the predicted and estimated values of every variable in the state to that
# variable's measured value.
def make_initial_filter_state(state):
    for var in (state.loc_state, state.head_state, state.SoG_state):
        var.est = var.meas
        var.pred = var.meas
    return state


# Initialize a var state object from a ais data point
# Remember, this will only initialize the MEASURED values
def make_state_from_deprecated_ais_data_format(data):
    loc_state = VarState(meas=data[0])
    head_state = VarState(meas=data[1])
    SoG_state = VarState(meas=data[2])
    return VesselState(loc_state=loc_state, head_state=head_state, SoG_state=SoG_state, timestamp=data[3])


def make_est_from_meas_pred_and_fact(meas, pred, fact):
    return np.add((1-fact)*pred, fact*meas)


def seconds_passed_between_states(curr_state:VesselState, prev_state:VesselState):
    return seconds_passed_between_datetimes(curr_state.timestamp, prev_state.timestamp)


def seconds_passed_between_datetimes(dt1: datetime, dt2: datetime):
    dv = dt1 - dt2
    return dv.total_seconds()


# Creates an ordered dict object from a list of fields and a list of values.
def row_to_dict(fields, row):
    row_dict = {}
    for i in range(len(fields)):
        row_dict[fields[i]] = row[i]
    return row_dict