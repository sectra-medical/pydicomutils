import os
import shutil
import glob
import logging

from pydicom import read_file
from utils.misc.dcm_io_helper import read_and_sort_dicom_files
from utils.scripts.convert_seg_to_gsps import convert_seg_to_gsps

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("pydicomutils_examples.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def run():
    logger.info("Running " + os.path.basename(__file__))
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Set output folder
    output_folder = os.path.join(output_folder, "data", "ct_images", "gsps_from_seg")
    os.makedirs(output_folder, exist_ok=True)

    # Find original images
    input_folder = os.path.join(
        file_folder, "data", "ct_images", "original_dicom_images"
    )
    dcm_files = glob.glob(os.path.join(input_folder, "*.dcm"))

    # Copy original images to output folder
    ds = read_file(dcm_files[0])
    dcm_folder = os.path.join(output_folder, "series_" + str(ds.SeriesNumber))
    os.makedirs(dcm_folder, exist_ok=True)
    for dcm_file in dcm_files:
        shutil.copy(dcm_file, dcm_folder)

    # Run conversion of seg to gsps
    input_file = glob.glob(
        os.path.join(file_folder, "data", "ct_images", "dcm_segmentation", "*.dcm")
    )[0]
    convert_seg_to_gsps(input_file, output_folder)


if __name__ == "__main__":
    run()
