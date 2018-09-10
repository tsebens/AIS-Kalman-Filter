from csv import DictReader
import numpy as np
from datetime import datetime
from calculate import unit_vector, vector_between_two_points, distance_between_two_points
from convert import seconds_passed_between_datetimes
from data_package import DataPackageBase
from conf.db import LON_FIELD_NAME, LAT_FIELD_NAME, TIMESTAMP_FIELD_NAME, OUTPUT_LAT_FIELD_NAME, OUTPUT_LON_FIELD_NAME, \
    OUTPUT_DEV_FIELD_NAME
from project import convert_aa_to_loc, convert_loc_to_aa
from state import VesselState, VarState
from conf.static import MAX_ALLOWABLE_VESSEL_SPEED
from timezones import UTC


def is_invalid(val):
    return np.isnan(val) or np.isinf(val)


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
    dev = distance_between_two_points(
        state.loc_state.meas,
        state.loc_state.est
    )
    row[OUTPUT_DEV_FIELD_NAME] = dev if not np.isnan(dev) else 0
    row[OUTPUT_LON_FIELD_NAME], row[OUTPUT_LAT_FIELD_NAME] = convert_aa_to_loc(state.loc_state.est[0], state.loc_state.est[1])
    row['flagged_by_filter'] = 1 if state.is_flagged else 0
    row['heading'] = state.head_state.est
    #row.pop('VMS_RECORD_ID')
    return row


def get_loc_from_vms(row, lat_fn: str=LAT_FIELD_NAME, lon_fn: str=LON_FIELD_NAME):
    lat = float(row[lat_fn])
    lon = float(row[lon_fn])
    lon, lat = convert_loc_to_aa(lon, lat)
    if is_invalid(lat):
        lat = 0
    if is_invalid(lon):
        lon = 0
    # VMS data is recorded in regular old geographic coordinates (ESPG:4326)
    # We want it in Alaska Albers, both because AA is measured in meters (works well for speed)
    # AND because AA is an equal-area conic projection, meaning we wont see any distortion of unit
    # lengths based on our latitude. Or at least not much.
    return np.array([lon, lat])


def get_head_from_vms(curr_row, prev_row, lat_fn: str=LAT_FIELD_NAME, lon_fn: str=LON_FIELD_NAME):
    prev_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    head = unit_vector(vector_between_two_points(prev_loc, curr_loc))
    if np.isnan(head[0]):
        head[0] = 0
    if np.isnan(head[1]):
        head[1] = 0
    return head


def get_SoG_from_vms(curr_row, prev_row, lat_fn: str=LAT_FIELD_NAME, lon_fn: str=LON_FIELD_NAME):
    prev_loc = get_loc_from_vms(prev_row, lat_fn=lat_fn, lon_fn=lon_fn)
    curr_loc = get_loc_from_vms(curr_row, lat_fn=lat_fn, lon_fn=lon_fn)
    # Since the location of the vessel is measured in meters, all we have to do is divide the
    # delta vector by the time it took to travers it to get the measured speed
    ts1 = get_timestamp_from_vms(curr_row)
    ts2 = get_timestamp_from_vms(prev_row)
    time = seconds_passed_between_datetimes(ts1, ts2)
    distance = distance_between_two_points(prev_loc, curr_loc)
    if time == 0:
        speed = 0
    else:
        speed = distance / time
        if np.isnan(speed):
            # If the values are small enough, our division will yield a NaN value, or an inf value. In that case we can
            # simply assign the value to zero
            speed = 0
        if np.isinf(speed):
            speed = MAX_ALLOWABLE_VESSEL_SPEED
    return speed


def make_timestamp_from_vms_value(timestamp):
    '''VMS format: 2018-04-16 00:00:00.0000000'''
    # TODO: This function is a huge problem. There are too many potential formats.
    if type(timestamp) == datetime:
        # If the data has been read from a database, there is a chance that it will already be in datetime format
        return timestamp
    date, time = timestamp.split(' ')
    try:
        year, month, day = date.split('-')
    except ValueError:
        day, month, year = date.split('/')
    try:
        hour, minute, second = time.split(':')
        second = int(float(second))
    except ValueError:
        hour, minute = time.split(':')
        second = 0
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), second=second, tzinfo=UTC)


def get_timestamp_from_vms(curr_row, ts_fn=TIMESTAMP_FIELD_NAME):
    return make_timestamp_from_vms_value(curr_row[ts_fn])


class CSV_VMSDataPackage(VMSDataPackage):
    def __init__(self, csv_fp: str):
        self.payload = None
        self.filtered_states = None
        self.csv_fp = csv_fp

    def load_payload(self):
        with open(self.csv_fp) as file:
            reader = DictReader(file) # todo: maybe this could be refactored to a factory method?
            self.payload = [row for row in reader]