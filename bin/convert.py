# Logic class for any conversions that need to be made
from math import tan, radians
import numpy as np
from datetime import datetime

from state import VarState, VesselState
from timezones import UTC

'''
Constants
'''
# knts * knts_to_mps_conv_fact = m/s
knts_to_mps_conv_fact = 0.51444444444

# Converts a true heading to a unit vector
def true_heading_to_unit_vector(point, head_fn='True_heading'):
    unit_v = np.array([1, tan(radians(float(point[head_fn])))])
    mag = np.linalg.norm(unit_v)
    unit_v = unit_v/mag
    unit_v = np.array([unit_v[1], unit_v[0]])
    return unit_v


def ais_timestamp_to_datetime(timestamp, tz=UTC):
    date, time = timestamp.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), second=int(second), tzinfo=tz)


def lat_lon_to_loc_vector(point, lat_fn='AA_LAT', lon_fn='AA_LON'):
    aa_lat = point[lat_fn]
    aa_lon = point[lon_fn]
    return np.array([aa_lat, aa_lon])


def sog(point, sog_fn='SOG__knts_'):
    return point[sog_fn]


def knts_to_mps(knts):
    return knts * knts_to_mps_conv_fact


# Makes a state in which for all VarStates, the estimated and predicted values are the same as the measured values
# Essentially make a state in which we must assume that the measured values are 100% accurate.
def make_initial_state_from_deprecated_ais_data_format(data):
    state = make_state_from_deprecated_ais_data_format(data)
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