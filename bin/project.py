# Projection logic
from pyproj import Proj
import numpy as np

aa_projection_init = "epsg:3338" # The epsg for Alaska Albers equal area conic
proj_aa = Proj(init=aa_projection_init) # Initiate a projection from cartographic coordinates to Alaska Albers


def convert_loc_to_aa(lon, lat):
    # Remember: LON, then LAT
    lon_aa, lat_aa = proj_aa(lon, lat)
    return lon_aa, lat_aa
