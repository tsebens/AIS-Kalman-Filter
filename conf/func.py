from static import KNTS_TO_MPS_CONV_FACT

# Convert knots to meters per second
def knts_to_mps(knts):
    return knts * KNTS_TO_MPS_CONV_FACT

def mps_to_knts(mps):
    return mps / KNTS_TO_MPS_CONV_FACT