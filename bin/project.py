# Projection logic
from pyproj import Proj

aa_projection_init = "epsg:3338" # The epsg for Alaska Albers equal area conic
proj_aa: Proj = Proj(init=aa_projection_init) # Initiate a projection from cartographic coordinates to Alaska Albers


def convert_loc_to_aa(lon, lat):
    # Remember: LON, then LAT
    lon_aa, lat_aa = proj_aa(lon, lat)
    return lon_aa, lat_aa


def convert_aa_to_loc(lon_aa, lat_aa):
    lon, lat = proj_aa(lon_aa, lat_aa, inverse=True)
    return lon, lat