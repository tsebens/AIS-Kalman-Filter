import unittest
import numpy as np
from matplotlib import pyplot as plt

from calculate import angle_between, rotate_vector


class TestCalculateMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_angle_between(self):
        v1 = np.array([0,1])
        v2 = np.array([1,0])
        assert(angle_between(v1, v2)==90.0)
        assert(angle_between(v2, v1)==90.0)

    def test_rotate_vector(self):
        v1 = np.array([0,1])
        rot = rotate_vector(v1, 90)
        # TODO: Finish this test. Remember that rotation does not produce an exact result.