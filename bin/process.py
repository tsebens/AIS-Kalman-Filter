from filter import ais_kalman
from conf.filter import filter_state
from vms import VMSDataPackage

def process_vessel(in_tbl_vessel, out_tbl_vessel):
    data_package = VMSDataPackage(in_tbl_vessel, out_tbl_vessel)
    data_package.load_payload()
    data_package.set_filtered_states(
        ais_kalman(
            data_package.get_states(),
            filter_state
        )
    )
    data_package.write_payload()