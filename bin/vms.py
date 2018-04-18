from datetime import datetime

import numpy as np

from calculate import unit_vector, vector_between_two_points, vector_length
from convert import seconds_passed_between_datetimes
from data import DataPackageBase
from project import convert_aa_to_loc, convert_loc_to_aa
from state import VesselState, VarState
from timezones import UTC


class VMSDataPackage(DataPackageBase):
    def make_state(self, curr_row, prev_row):
        return make_vessel_state_from_vms_rows(curr_row, prev_row)

    def make_init_state(self, init_row):
        return make_init_state_from_vms(init_row)

    def make_row(self, state):
        return make_row_from_vms_state(state)


def make_vessel_state_from_vms_rows(curr_row, prev_row):
    return VesselState(
        loc_state=VarState(
            meas=get_loc_from_vms(curr_row)
        ),
        head_state=VarState(
            meas=get_head_from_vms(curr_row, prev_row)
        ),
        SoG_state=VarState(
            meas=get_SoG_from_vms(curr_row, prev_row)
        ),
        timestamp=get_timestamp_from_vms(curr_row),
        row=curr_row
    )


def make_init_state_from_vms(init_row):
    return VesselState(
        loc_state=VarState(
            meas=get_loc_from_vms(init_row)
        ),head_state=VarState(
            meas=np.array([0,0])
        ),
        SoG_state=VarState(
            meas=0
        ),
        timestamp=get_timestamp_from_vms(init_row),
        row=init_row
    )


def make_row_from_vms_state(state: VesselState):
    row = state.row
    row['filt_lon'], row['filt_lat'] = convert_aa_to_loc(state.loc_state.est[0], state.loc_state.est[1])
    return row


def get_loc_from_vms(row, lat_fn: str='latitude', lon_fn: str='longitude'):
    lat = float(row[lat_fn])
    lon = float(row[lon_fn])
    lon, lat = convert_loc_to_aa(lon, lat)
    # VMS data is recorded in regular old geographic coordinates (ESPG:4326)
    # We want it in Alaska Albers, both because AA is measured in meters (works well for speed)
    # AND because AA is an equal-area conic projection, meaning we wont see any distortion of unit
    # lengths based on our latitude. Or at least not much.
    return np.array([lon, lat])


def get_head_from_vms(curr_row, prev_row, lat_fn='latitude', lon_fn='longitude'):
    prev_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    return unit_vector(vector_between_two_points(prev_loc, curr_loc))


def get_SoG_from_vms(curr_row, prev_row, lat_fn: str ='latitude', lon_fn: str ='longitude'):
    prev_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    # Since the location of the vessel is measured in meters, all we have to do is divide the
    # delta vector by the time it took to travers it to get the measured speed
    ts1 = get_timestamp_from_vms(curr_row)
    ts2 = get_timestamp_from_vms(prev_row)
    time_passed = seconds_passed_between_datetimes(ts1, ts2)
    return vector_length(vector_between_two_points(prev_loc, curr_loc))/time_passed


def make_timestamp_from_vms_value(timestamp):
    if type(timestamp) == datetime:
        # If the data has been read frm a database, then it will already be in datetime
        return timestamp
    date, time = timestamp.split(' ')
    month, day, year = date.split('/')
    hour, minute = time.split(':')
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), tzinfo=UTC)


def get_timestamp_from_vms(curr_row, ts_fn='position_datetime'):
    return make_timestamp_from_vms_value(curr_row[ts_fn])