from collections import OrderedDict

from connect import TableVessel
from exceptions import NoTableConnectionSpecified, UseOfAbstractForm, AttemptToWriteUnprocessedData, \
    AttemptToReadUnprocessedData


# TODO: Still needs a fair amount of work ironing out the data loading process.
from state import VesselState


class DataPackageBase:
    def __init__(self, in_tbl_vessel: TableVessel=None, out_tbl_vessel: TableVessel=None):
        self.payload = None
        self.filtered_states = None
        self.in_tbl_conn = in_tbl_vessel
        self.out_tbl_conn = out_tbl_vessel

    def load_payload(self):
        """Loads the DataPackage with all of the data from the DB table"""
        # TODO: In the future, this should set the payload as a generator supplied by the TableConnection
        # The generator should in turn reference a buffered generator from within the TableConnection
        if self.in_tbl_conn is None:
            raise NoTableConnectionSpecified('Attempted to load data into DataPackage, but no TableConnection has been specified.')
        self.payload = self.in_tbl_conn.get_data()

    def write_payload(self):
        """Write the filtered states"""
        if self.out_tbl_conn is None:
            raise NoTableConnectionSpecified('Attempted to write DataPackage payload to DB, but no TableConnection has been specified.')
        if self.filtered_states is None:
            raise AttemptToWriteUnprocessedData('Attempted to write to the DB, but the data hasn\'t been processed yet.')
        self.out_tbl_conn.write_data(self.make_rows(self.payload))

    def get_payload(self):
        """Return the payload as a list of OrderedDicts"""
        return self.payload

    def set_payload(self, data):
        """Set payload to a collection of OrderedDicts"""
        self.payload = data

    def get_states(self):
        """Return a list of VesselStates that have been built from the DataPackage's payload"""
        init_row_1 = self.payload[0]
        init_row_2 = self.payload[1]
        vs1, vs2 = self.make_init_states(init_row_1, init_row_2)
        states = [vs1, vs2]
        prev_row = init_row_2
        for curr_row in self.payload[2:]:
            states.append(self.make_state(curr_row, prev_row))
            prev_row = curr_row
        return states

    def get_filtered_states(self, filter):
        """Apply the passed filter function to the DataPackage's states, then return them"""
        return filter(self.get_states())

    def make_state(self, curr_row, prev_row):
        raise UseOfAbstractForm('Attempted to use abstract version of DataPackage.make_state. Must use a child class')

    def make_init_states(self, init_row_1: OrderedDict, init_row_2: OrderedDict):
        raise UseOfAbstractForm('Attempted to use abstract version of DataPackage.make_init_state. Must use a child class')

    def make_rows(self, states):
        return [self.make_row(state) for state in states]

    def make_row(self, state):
        raise UseOfAbstractForm('Attempted to use abstract version of DataPackage.make_row. Must use a child class')
