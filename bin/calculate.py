from math import fabs
import numpy as np

from state import VesselState

"""Assorted calculation functions needed around the application."""

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2, abs=True):
    """ Returns the angle in degrees between vectors 'v1' and 'v2'"""
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    ang = np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))
    if abs:
        ang = fabs(ang)
    return ang


def rotate_vector(v1, deg):
    """Rotate the given vector by deg degrees counter-clockwise"""
    theta = np.radians(deg)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    v2 = np.matmul(R, v1)
    return v2


# Returns the vector pointing from p1 to p2
def vector_between_two_points(p1, p2):
    res = np.subtract(p1, p2)
    return res


# Return the length of a vector
def vector_length(v1):
    return np.linalg.norm(v1)


def distance_between_two_states(s1: VesselState, s2: VesselState):
    """Return the distance between the observed locations between two states"""
    return distance_between_two_points(s1.loc_state.meas, s2.loc_state.meas)


def distance_between_two_points(p1, p2):
    if np.all(np.isclose(p1, p2)):
        return 0
    return vector_length(vector_between_two_points(p1,p2))
    
    
def rmse(predictions, targets):
    """Returns the root mean squared error of two sets of points"""
    diff = np.subtract(np.array(predictions), np.array(targets))
    rmse = np.sqrt(diff ** 2).mean()
    if np.isnan(rmse):
        return 0
    if np.isinf(rmse):
        return 'inf'
    return rmse
    
    
def rmse_of_states(states):
    return rmse(
        [state.loc_state.est for state in states],
        [state.loc_state.meas for state in states]
    )