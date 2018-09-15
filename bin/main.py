import sys
from builtins import StopIteration
from csv import DictWriter

from os import getcwd
from os.path import join


cwd = getcwd()
sys.path.append(join(cwd, '..'))
static_wd = r'F:\CIA_Python\PROD\PythonScripts\AIS-Kalman-Filter'
cwd = static_wd
sys.path.append(cwd) # We do this because SQL Server calls this script from a different working directory
sys.path.append(join(cwd, 'bin'))
sys.path.append(join(cwd, 'conf'))
from data_package import DataPackageBase
from conf.db import ID_FIELD, OUTPUT_TABLE, INPUT_TABLE, TIMESTAMP_FIELD, db
from conf.filter import filter_state
from connect import TableVessel
from vms import VMSDataPackage, CSV_VMSDataPackage
from filter import ais_kalman, pre_process_data


def main():
    db.test_connection()
    # Compile a list of all unique entities in the table to test, then iterate through them
    ids = db.get_unique_elements(INPUT_TABLE, ID_FIELD)
    for id_val in ids:
        try:
            print('Processing %s' % id_val)
            # Define the input and output points for the data
            data_package = VMSDataPackage(
                TableVessel(db, INPUT_TABLE, id_field=ID_FIELD, id_value=id_val, order_field=TIMESTAMP_FIELD),
                TableVessel(db, OUTPUT_TABLE, id_field=ID_FIELD, id_value=id_val, order_field=TIMESTAMP_FIELD)
            )
            print('Loading payload...')
            # Load the data into memory
            data_package.load_payload()
            print('Preprocessing data...')
            # Preprocess the data to attempt to remove
            data_package.set_payload(pre_process_data(data_package.get_payload()))
            print("Filtering data...")
            # Filter the data
            data_package.set_payload(ais_kalman(data_package.get_payload(), filter_state))
            print('Writing payload...')
            # Write the filtered data back.
            data_package.write_payload()
        except StopIteration:
            print('Empty dataset')
            continue


def filter_vms_csv(csv):
    """Filter the contents of a csv file"""
    dp = CSV_VMSDataPackage(csv)
    dp = filter_dp(dp)
    with open(r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\bad_data_out.csv', 'w', newline='') as out:
        filtered_states = dp.make_rows(dp.get_payload())
        init = filtered_states[0]
        writer = DictWriter(out, fieldnames=init.keys())
        writer.writeheader()
        writer.writerow(init)
        for row in filtered_states[1:]:
            writer.writerow(row)


def filter_dp(dp: DataPackageBase):
    """Run the contents of a DataPackage through the filter"""
    dp.load_payload()
    dp.set_payload(ais_kalman(dp.get_states(), filter_state))
    return dp


def test_bad_data():
    fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\bad_data.csv'
    filter_vms_csv(fp)

if __name__ == '__main__':
     main()
