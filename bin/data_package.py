from collections import OrderedDict

from connect import TableVessel
from exceptions import NoTableConnectionSpecified, UseOfAbstractForm, AttemptToWriteUnprocessedData, \
    AttemptToReadUnprocessedData


# TODO: Still needs a fair amount of work ironing out the data loading process.
class DataPackageBase:
    def __init__(self, in_tbl_vessel: TableVessel=None, out_tbl_vessel: TableVessel=None):
        self.payload = None
        self.filtered_states = None
        self.in_tbl_conn = in_tbl_vessel
        self.out_tbl_conn = out_tbl_vessel

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
        print('Filtered state row:\n%s' % self.make_row(self.filtered_states[0]))
        self.out_tbl_conn.write_data(self.make_rows(self.filtered_states))

    # Returns the values of the payload as a generator of OrderedDicts
    def get_payload(self):
        # TODO: In the future, self.payload will reference a generator supplied by the TableConnection.
        # This loop will still work
        for row in self.payload:
            yield row

    def get_states(self):
        payload_gen = self.get_payload()
        init_row_1 = payload_gen.__next__()
        init_row_2 = payload_gen.__next__()
        vs1, vs2 = self.make_init_states(init_row_1, init_row_2)
        yield vs1
        yield vs2
        prev_row = init_row_2
        for curr_row in payload_gen:
            yield self.make_state(curr_row, prev_row)
            prev_row = curr_row

    def set_filtered_states(self, states):
        self.filtered_states = states

    def get_filtered_states(self):
        if self.filtered_states is None:
            raise AttemptToReadUnprocessedData('Attempted to read filtered data before it has been filtered.')
        return self.filtered_states

    def make_state(self, curr_row, prev_row):
        raise UseOfAbstractForm('Attempted to use abstract version of make_state. Must use a child class')

    def make_init_states(self, init_row_1: OrderedDict, init_row_2: OrderedDict):
        raise UseOfAbstractForm('Attempted to use abstract version of make_init_state. Must use a child class')

    def make_rows(self, states):
        return [self.make_row(state) for state in states]

    def make_row(self, state):
        raise UseOfAbstractForm('Attempted to use abstract version of make_row. Must use a child class')
