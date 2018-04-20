class NoTableConnectionSpecified(Exception):
    pass


class UseOfAbstractForm(Exception):
    pass


class AttemptToWriteUnprocessedData(Exception):
    pass


class AttemptToReadUnprocessedData(Exception):
    pass