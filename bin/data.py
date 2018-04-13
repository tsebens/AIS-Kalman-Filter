from collections import OrderedDict
from datetime import datetime
from random import randint
from csv import DictReader, DictWriter
from os import listdir
from os.path import join
from typing import List

import numpy as np

from calculate import vector_between_two_points, vector_length, unit_vector
from connect import TableConnection, retrieve_table_data, connect_to_db
from convert import lat_lon_to_loc_vector, true_heading_to_unit_vector, ais_sog, ais_timestamp_to_datetime, \
    knts_to_mps, seconds_passed_between_datetimes
from project import convert_loc_to_aa, convert_aa_to_loc
from state import VesselState, VarState
from timezones import UTC

'''
----------------------------------------------------------------
Constants
----------------------------------------------------------------
'''
# The directory where all grouped ais data will be stored
data_dir = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\data'

# The directory where all downloaded OrbComm AIS data can be found
orbcomm_dir = r'C:\Users\tristan.sebens\Projects\OrbCommInterface\downloads'
'''
----------------------------------------------------------------
'''


class NoTableConnectionSpecified(Exception):
    pass


class UseOfAbstractForm(Exception):
    pass


class AttemptToWriteUnprocessedData(Exception):
    pass


# TODO: Still needs a fair amount of work ironing out the data loading process.
class DataPackageBase:
    def __init__(self, in_tbl_conn: TableConnection=None, out_tbl_conn: TableConnection=None):
        self.payload = None
        self.filtered_states = None
        self.in_tbl_conn = in_tbl_conn
        self.out_tbl_conn = out_tbl_conn

    # Loads the DataPackage with all of the data from the DB table
    def load_payload(self):
        # TODO: In the future, this should set the payload as a generator supplied by the TableConnection
        # The generator should in turn reference a buffered generator from within the TableConnection
        if self.in_tbl_conn is None:
            raise NoTableConnectionSpecified('Attempted to load data into DataPackage, but no TableConnection has been specified.')
        self.payload = self.in_tbl_conn.get_data()

    def write_payload(self):
        if self.out_tbl_conn is None:
            raise NoTableConnectionSpecified('Attempted to write DataPackage payload to DB, but not TableConnection has been specified.')
        if self.filtered_states is None:
            raise AttemptToWriteUnprocessedData('Attempted to write to the DB, but the data hasn\'t been processed yet.')
        self.out_tbl_conn.write_data(self.make_rows(self.filtered_states))

    # Returns the values of the payload as a generator of OrderedDicts
    def get_payload(self):
        # TODO: In the future, self.payload will reference a generator supplied by the TableConnection.
        # This loop will still work
        for row in self.payload:
            yield row

    def get_states(self):
        payload_gen = self.get_payload()
        prev_row = payload_gen.__next__()
        yield self.make_init_state(prev_row)
        for curr_row in payload_gen:
            yield self.make_state(curr_row, prev_row)
            prev_row = curr_row

    def set_filtered_states(self, states):
        self.filtered_states = states;

    def make_state(self, curr_row, prev_row):
        raise UseOfAbstractForm('Attempted to use abstract version of make_state. Must use a child class')

    def make_init_state(self, init_row):
        raise UseOfAbstractForm('Attempted to use abstract version of make_init_state. Must use a child class')

    def make_rows(self, states):
        return [self.make_row(state) for state in states]

    def make_row(self, state):
        raise UseOfAbstractForm('Attempted to use abstract version of make_row. Must use a child class')


class VMSDataPackage(DataPackageBase):
    def make_state(self, curr_row, prev_row):
        return make_vessel_state_from_vms_rows(curr_row, prev_row)

    def make_init_state(self, init_row):
        return make_init_state_from_vms(init_row)

    def make_row(self, state):
        return make_row_from_vms(state)


class AISDataPackage(DataPackageBase):
    def make_state(self, curr_row, prev_row):
        return make_vessel_state_from_ais_rows(curr_row, prev_row)

    def make_init_state(self, init_row):
        return make_vessel_state_from_ais_rows(init_row, None)


# TODO: The following function needs to be updated with the correct configuration for AIS data files
def get_loc_from_ais(curr_row: OrderedDict):
    lat = float(curr_row['Latitude'])
    lon = float(curr_row['Longitude'])
    return np.array(lat, lon)


# TODO: The following function needs to be updated with the correct configuration for AIS data files
def get_head_from_ais(curr_row):
    return true_heading_to_unit_vector(float(curr_row['True heading']))


# TODO: The following function needs to be updated with the correct configuration for AIS data files
def get_SoG_from_ais(curr_row):
    return curr_row['Speed over ground']


# TODO: The following function needs to be updated with the correct configuration for AIS data files
def get_timestamp_from_ais(curr_row):
    # TODO: There is the theoretical possibility of the row containing a timestamp as a string, not a datetime object.
    # This function needs to account for that somehow.
    return curr_row['timestamp']


def make_vessel_state_from_ais_rows(curr_row, prev_row):
    return VesselState(
        loc_state=VarState(
            meas=get_loc_from_ais(curr_row)
        ),
        head_state=VarState(
            meas=get_head_from_ais(curr_row)
        ),
        SoG_state=VarState(
            meas=get_SoG_from_ais(curr_row)
        ),
        timestamp=get_timestamp_from_ais(curr_row),
        row = curr_row
    )


def make_states_from_vms_data(data):
    prev_row = data.__next__()
    states = [make_init_state_from_vms(prev_row),]
    for curr_row in data:
        states.append(make_vessel_state_from_vms_rows(curr_row, prev_row))
        prev_row = curr_row
    return states


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

def make_row_from_vms(state: VesselState):
    row: OrderedDict = state.row
    row['filt_lon'], row['filt_lat'] = convert_aa_to_loc(state.loc_state.est[0], state.loc_state.est[1])
    return row

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


# Convert a timestamp of the format 1/1/2010 0:33 to a datetime object
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
