import numpy as np
from datetime import datetime
from calculate import unit_vector, vector_between_two_points, vector_length
from convert import seconds_passed_between_datetimes
from data_package import DataPackageBase
from project import convert_aa_to_loc, convert_loc_to_aa
from state import VesselState, VarState
from timezones import UTC


class VMSDataPackage(DataPackageBase):
    def make_state(self, curr_row, prev_row):
        return make_vessel_state_from_vms_rows(curr_row, prev_row)

    def make_init_states(self, init_row_1, init_row_2):
        return make_init_state_from_vms(init_row_1, init_row_2)

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


def make_init_state_from_vms(init_row_1, init_row_2):
    heading = get_head_from_vms(init_row_2, init_row_1)
    SoG = get_SoG_from_vms(init_row_2, init_row_1)
    vs1 = VesselState(
        loc_state=VarState(
            meas=get_loc_from_vms(init_row_1)
        ), head_state=VarState(
            meas=heading
        ),
        SoG_state=VarState(
            meas=SoG
        ),
        timestamp=get_timestamp_from_vms(init_row_1),
        row=init_row_1
    )
    vs2 = VesselState(
        loc_state=VarState(
            meas=get_loc_from_vms(init_row_2)
        ),head_state=VarState(
            meas=heading
        ),
        SoG_state=VarState(
            meas=SoG
        ),
        timestamp=get_timestamp_from_vms(init_row_2),
        row=init_row_2
    )
    return vs1, vs2



def make_row_from_vms_state(state: VesselState):
    row = state.row
    row['filt_lon'], row['filt_lat'] = convert_aa_to_loc(state.loc_state.est[0], state.loc_state.est[1])
    return row


def get_loc_from_vms(row, lat_fn: str='LATITUDE', lon_fn: str='LONGITUDE'):
    lat = float(row[lat_fn])
    lon = float(row[lon_fn])
    lon, lat = convert_loc_to_aa(lon, lat)
    # VMS data is recorded in regular old geographic coordinates (ESPG:4326)
    # We want it in Alaska Albers, both because AA is measured in meters (works well for speed)
    # AND because AA is an equal-area conic projection, meaning we wont see any distortion of unit
    # lengths based on our latitude. Or at least not much.
    return np.array([lon, lat])


def get_head_from_vms(curr_row, prev_row, lat_fn='LATITUDE', lon_fn='LONGITUDE'):
    prev_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    return unit_vector(vector_between_two_points(prev_loc, curr_loc))


def get_SoG_from_vms(curr_row, prev_row, lat_fn: str ='LATITUDE', lon_fn: str ='LONGITUDE'):
    prev_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    # Since the location of the vessel is measured in meters, all we have to do is divide the
    # delta vector by the time it took to travers it to get the measured speed
    ts1 = get_timestamp_from_vms(curr_row)
    ts2 = get_timestamp_from_vms(prev_row)
    time_passed = seconds_passed_between_datetimes(ts1, ts2)
    return vector_length(vector_between_two_points(prev_loc, curr_loc))/time_passed


def make_timestamp_from_vms_value(timestamp):
    '''VMS format: 2018-04-16 00:00:00.0000000'''
    if type(timestamp) == datetime:
        # If the data has been read frm a database, then it will already be in datetime
        return timestamp
    date, time = timestamp.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), second=int(float(second)), tzinfo=UTC)


def get_timestamp_from_vms(curr_row, ts_fn='POSITION_DATETIME'):
    return make_timestamp_from_vms_value(curr_row[ts_fn])