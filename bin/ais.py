from collections import OrderedDict

import numpy as np

from convert import true_heading_to_unit_vector
from data_package import DataPackageBase
from state import VesselState, VarState


class AISDataPackage(DataPackageBase):
    def make_state(self, curr_row, prev_row):
        return make_vessel_state_from_ais_rows(curr_row, prev_row)

    def make_init_state(self, init_row):
        return make_vessel_state_from_ais_rows(init_row, None)

    def make_row(self, state):
        return make_row_from_ais_state()


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
        row=curr_row
    )


# TODO: All of these functions need to be updated with the correct fieldnames.
def get_loc_from_ais(curr_row: OrderedDict):
    lat = float(curr_row['Latitude'])
    lon = float(curr_row['Longitude'])
    return np.array(lat, lon)


def get_head_from_ais(curr_row):
    return true_heading_to_unit_vector(float(curr_row['True heading']))


def get_SoG_from_ais(curr_row):
    return curr_row['Speed over ground']


def get_timestamp_from_ais(curr_row):
    # TODO: There is the theoretical possibility of the row containing a timestamp as a string, not a datetime object.
    # This function needs to account for that somehow.
    return curr_row['timestamp']


def make_row_from_ais_state(state: VesselState):
    row = state.row
    row['filt_lat'] = state.loc_state.est[1]
    row['filt_lon'] = state.loc_state.est[0]
    row['filt_sog'] = state.SoG_state.est
    row['filt_head'] = state.head_state.est


