from random import randint
from csv import DictReader, DictWriter
from os import listdir
from os.path import join
from convert import lat_lon_to_loc_vector, true_heading_to_unit_vector, sog, ais_timestamp_to_datetime

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
        ais_data.extend(pull_data_from_ais_csv(fp))
    return ais_data


# Read all ais_data in a single csv file and return that ais_data as a list of dicts
def pull_data_from_ais_csv(fp):
    with open(fp) as file:
        reader = DictReader(file)
        ais_data = [row for row in reader]
    return ais_data


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
        heading = true_heading_to_unit_vector(point)
        SoG = sog(point)
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


def get_rand_ais_data_point():
    fps = [join(data_dir, f) for f in listdir(data_dir)]
    fp = fps[randint(0, len(fps))]
    with open(fp) as file:
        reader = DictReader(file)
        data = [row for row in reader]
    return data[randint(0, len(data))]