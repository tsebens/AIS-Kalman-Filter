import sys
from builtins import StopIteration
from csv import DictWriter

from os import getcwd, listdir
from os.path import join, splitext, basename

from data_package import DataPackageBase
from plot import clear, show_plot
from calculate import rmse_of_states

cwd = getcwd()
sys.path.append(join(cwd, '..'))
static_wd = r'F:\CIA_Python\PROD\PythonScripts\AIS-Kalman-Filter'
cwd = static_wd
sys.path.append(cwd) # We do this because SQL Server calls this script from a different working directory
sys.path.append(join(cwd, 'bin'))
sys.path.append(join(cwd, 'conf'))
from plot import make_iterative_plot, make_plot
from conf.db import server, port, dbname, user, pwd, ID_FIELD, OUTPUT_TABLE, INPUT_TABLE, TIMESTAMP_FIELD
from conf.filter import filter_state
from connect import TableVessel, SQLServerDataBase, PostgreSQLDataBase
from pypika import Table, Field
from vms import VMSDataPackage, CSV_VMSDataPackage
from filter import ais_kalman

def main():
    vms_table = Table('STG_VMS', schema='dbo')
    id_field = Field('VESSEL_ID')
    db = SQLServerDataBase(server, port, dbname, '', '', trusted_source=True)
    db.test_connection()
    ids = db.get_unique_elements(vms_table, id_field)
    count = 0
    for id_val in ids:
        try:
            print('Processing %s' % id)
            in_tbl_vessel = TableVessel(db, INPUT_TABLE, id_field=ID_FIELD, id_value=id_val)
            out_tbl_vessel = TableVessel(db, OUTPUT_TABLE, id_field=ID_FIELD, id_value=id_val)
            data_package = VMSDataPackage(in_tbl_vessel, out_tbl_vessel)
            print('Loading payload...')
            data_package.load_payload()
            print("Filtering data...")
            data_package.set_filtered_states(ais_kalman(data_package.get_states(), filter_state))
            print('Writing payload...')
            data_package.write_payload()
        except StopIteration:
            print('Empty dataset')
            continue


def filter_vms_csv(csv):
    """Filter the contents of a csv file"""
    dp = CSV_VMSDataPackage(csv)
    dp = filter_dp(dp)
    with open(r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\bad_data_out.csv', 'w', newline='') as out:
        filtered_states = dp.make_rows(dp.get_filtered_states())
        init = filtered_states[0]
        writer = DictWriter(out, fieldnames=init.keys())
        writer.writeheader()
        writer.writerow(init)
        for row in filtered_states[1:]:
            writer.writerow(row)


def filter_dp(dp: DataPackageBase):
    """Run the contents of a DataPackage through the filter"""
    dp.load_payload()
    dp.set_filtered_states(ais_kalman(dp.get_states(), filter_state))
    return dp


def test_bad_data():
    fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\bad_data.csv'
    filter_vms_csv(fp)

if __name__ == '__main__':
    test_bad_data()
