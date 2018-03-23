import unittest

from estimation import est_SoG_max_spd
from state import VesselState, VarState


class TestEstimateMethods(unittest.TestCase):

    def setUp(self):
        zero_state = VesselState(
            loc_state=VarState(
                meas=0,
                pred=0,
                est=0,
            ),
            head_state=VarState(
                meas=0,
                pred=0,
                est=0
            ),
            SoG_state=VarState(
                meas=0,
                pred=0,
                est=0
            )
        )

    def test_est_SoG_max_spd(self):
        result = est_SoG_max_spd()