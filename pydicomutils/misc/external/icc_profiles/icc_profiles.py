import os

def get_sRGB_icc_profile():
    """Utility functions that reads the sRGB profile
    """
    file_folder = os.path.dirname(os.path.realpath(__file__))
    rgb_icc_profile = None
    with open(os.path.join(file_folder, "sRGB2014.icc"), "rb") as f:
        rgb_icc_profile = f.read()
    return rgb_icc_profile