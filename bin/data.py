from datetime import datetime
from random import randint
from csv import DictReader, DictWriter
from os import listdir
from os.path import join

import numpy as np

from calculate import vector_between_two_points, vector_length, unit_vector
from convert import lat_lon_to_loc_vector, true_heading_to_unit_vector, ais_sog, ais_timestamp_to_datetime, \
    knts_to_mps, seconds_passed_between_datetimes
from project import convert_loc_to_aa
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

# Reads all ais data available in a directory and returns it as a single list of dicts
def pull_ais_data_from_dir(d):
    files = [join(d, f) for f in listdir(d)]
    ais_data = []
    for fp in files:
        ais_data.extend(pull_data_from_csv(fp))
    return ais_data


# Read all ais_data in a single csv file and return that ais_data as a list of dicts
def pull_data_from_csv(fp):
    with open(fp) as file:
        reader = DictReader(file)
        for row in reader:
            yield row


# Groups ais ais_data by it's MMSI ais_data. Returns a list of dicts. Each dict consists of a single key/value pair, where the
# key is a given MMSI number, and the value is another list of dicts containing all of the AIS data points of that
# MMSI number
def group_ais_data_by_mmsi(ais_data):
    mmsi_dict = {}
    for row in ais_data:
        if row['MMSI'] in mmsi_dict.keys():
            mmsi_dict[row['MMSI']].append(row)
        else:
            mmsi_dict[row['MMSI']] = [row,]
    return mmsi_dict


# Record ais data which has been grouped by its MMSI values
# Each unique MMSI number will have all data associated with it collected into a single file
def record_grouped_ais_data(ais_data):
    for mmsi in ais_data:
        data = ais_data[mmsi]
        out_fp = join(data_dir, mmsi + '.csv')
        record_ais_data(data, out_fp)


# Record all of the data contained in ais_data into a file at fp
# ais_data must be a dict-list (essentially a db table)
def record_ais_data(ais_data, fp):
    fieldnames = ais_data[0].keys()
    with open(fp, 'w', newline='') as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ais_data)


# Retrieves all ais data from a specified directory
def get_ais_data_from_dir(d):
    ais_data = pull_ais_data_from_dir(d)
    grouped = group_ais_data_by_mmsi(ais_data)
    record_grouped_ais_data(grouped)


# Retrieve any and all available AIS data from the OrbComm directory
def get_ais_data_from_orbcomm():
    get_ais_data_from_dir(orbcomm_dir)


# Conversion function. Accepts raw AIS ais_data as provided by OrbComm and outputs the ais_data in the format specified and
# expected by the kalman filter.
def convert_ais_data_to_usable_form(fp):
    with open(fp) as file:
        reader = DictReader(file)
        ais = [row for row in reader]
    for point in ais:
        loc = lat_lon_to_loc_vector(point)
        heading = true_heading_to_unit_vector(point, head_fn='AVERAGE_BEARING')
        # AIS SOG data comes in knots. We want mps
        SoG = knts_to_mps(ais_sog(point))
        time = ais_timestamp_to_datetime(point['Date_time_stamp'])
        # Yield the result of our formatting as a single data point in the format that the filter expects.
        yield (loc, heading, SoG, time)


# Order ais ais_data by timestamp, so that all ais_data points are in chronological order.
# This function assumes that the incoming ais_data is unformatted ais_data from OrbComm
def order_ais_data_by_ts(ais_data, ts_label='Date_time_stamp'):
    # While sorting, each data point has its timestamp converted to a datetime object in situ for comparison
    # This does not alter the recorded value for the point's timestamp. It remains in the OrbComm timestamp format.
    return sorted(ais_data, key=lambda p: ais_timestamp_to_datetime(p[ts_label]))


# Reorders an ais data csv file to be in chronological order
# This turns out to not be necessary for data downloaded from OrbComm, as the points are already in order, even after
# they are grouped by their MMSI numbers
def reorder_ais_csv(fp):
    with open(fp) as file:
        reader = DictReader(file)
        fieldnames = reader.fieldnames
        data = [l for l in reader]
    with open(fp, 'w', newline='') as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(order_ais_data_by_ts(data))


# Returns a single random AIS point from the the AIS data directory
def get_rand_ais_data_point():
    fps = [join(data_dir, f) for f in listdir(data_dir)]
    fp = fps[randint(0, len(fps))]
    with open(fp) as file:
        reader = DictReader(file)
        data = [row for row in reader]
    return data[randint(0, len(data))]

# TODO: Add function that accepts a list of VesselState objects and outputs a CSV file formatted identically to the AIS data.
# Thinking about it, this probably means that all of the data will need to be stored in the states, not just the relevant data.
# Everything that isn't relevant can be stored in a sub-object called 'junk' or something.


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


def get_timestamp_from_vms(curr_row, ts_fn='POSITION_DATETIME'):
    return make_timestamp_from_vms_value(curr_row[ts_fn])


def convert_vsm_data_to_states(fp):
    data = pull_data_from_csv(fp)
    prev_row = data.__next__()
    states = []
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
        timestamp=get_timestamp_from_vms(curr_row)
    )


def separate_vms_data_by_vessel_id(data, id_fn='VESSEL_ID'):
    data_by_id = {}
    for row in data:
        id = row[id_fn]
        if id in data_by_id.keys():
            data_by_id[id].append(row)
        else:
            data_by_id[id] = [row,]
    return data_by_id


def record_vms_data_by_vessel_id(in_fp, out_dir, id_fn='VESSEL_ID'):
    data = pull_data_from_csv(in_fp)
    data_sep = separate_vms_data_by_vessel_id(data, id_fn=id_fn)
    for vessel_id in data_sep:
        vessel_data = data_sep[vessel_id]
        out_fp = join(out_dir, vessel_id + '.csv')
        with open(out_fp, 'w', newline='') as file:
            fns = vessel_data[0].keys()
            writer = DictWriter(file, fieldnames=fns)
            writer.writeheader()
            writer.writerows(vessel_data)
