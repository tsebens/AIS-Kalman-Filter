import sys
from os import getcwd, listdir
from os.path import join, splitext, basename

from plot import clear, show_plot
from calculate import root_mean_squared_error

cwd = getcwd()
sys.path.append(join(cwd, '..'))
from plot import make_iterative_plot, make_plot
from conf.db import server, port, dbname, user, pwd, ID_FIELD, OUTPUT_TABLE, INPUT_TABLE
from conf.filter import filter_state
from connect import TableVessel, SQLServerDataBase, PostgreSQLDataBase
from vms import VMSDataPackage, CSV_VMSDataPackage
from filter import ais_kalman




d = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\by_id'
ph_d = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\diagrams'
files = [join(d, f) for f in listdir(d) if splitext(f)[1]=='.csv']
data_packages = [CSV_VMSDataPackage(file) for file in files]
for data_package in data_packages:
    fname = splitext(basename(data_package.csv_fp))[0]
    if fname != '3396':
        continue
    print('Processing %s' % fname)
    data_package.load_payload()
    data_package.set_filtered_states(ais_kalman(data_package.get_states(), filter_state))
    rms = root_mean_squared_error(
        [state.loc_state.meas for state in data_package.filtered_states],
        [state.loc_state.est  for state in data_package.filtered_states]
        )
    name = 'RMSE - %s ID - %s' % (rms, fname)
    out_fp = join(ph_d, name + '.png')
    make_plot(data_package.get_filtered_states(), title='RMS: %s' % rms)
    show_plot()
    clear()

'''
db = PostgreSQLDataBase(server, port, dbname, user, pwd, verbose=True)
db.test_connection()
in_table = INPUT_TABLE
out_table = OUTPUT_TABLE
ids = db.get_unique_elements(in_table, ID_FIELD)
for id in ids:
    in_table_vessel = TableVessel(db, in_table, id_field=ID_FIELD, id_value=id)
    out_table_vessel = TableVessel(db, out_table, id_field=ID_FIELD, id_value=id)
    data_package = VMSDataPackage(in_tbl_vessel=in_table_vessel, out_tbl_vessel=out_table_vessel)
    print("Loading values from DB")
    data_package.load_payload()
    print("Performing filter")
    data_package.set_filtered_states(ais_kalman(data_package.get_states(), filter_state))
    make_iterative_plot(data_package.get_filtered_states(), delay=0.1)
    input('Press enter to exit')
    sys.exit()
#data_package.write_payload()
'''