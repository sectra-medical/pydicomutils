import os
import random
from datetime import datetime
from math import pow
import numpy as np
from skimage.transform import resize
from skimage import data
from imageio import imread
import requests
import logging

from pydicom.uid import generate_uid

from pydicomutils.IODs.SCImage import SCImage

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
    logger.info("Starting") 
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Simple example with a BW test image from skimage
    logger.info("Simple 512x512 example from skimage")
    sc_image = SCImage()
    sc_image.create_empty_iod()
    sc_image.initiate()
    sc_image.set_dicom_attribute("PatientName", "BWBrick^512x512")
    sc_image.set_dicom_attribute("SeriesNumber", "1")
    sc_image.add_pixel_data(data.brick())
    study_folder = os.path.join(output_folder, "data", "sc_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "brick_512x512"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "brick_512x512", 
                                str(sc_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    sc_image.write_to_file(output_file)

    # Simple example with an RGB test image from skimage
    logger.info("RGB example from skimage")
    sc_image = SCImage()
    sc_image.create_empty_iod()
    sc_image.initiate()
    sc_image.set_dicom_attribute("PatientName", "RGBRetina^NoTiling")
    sc_image.set_dicom_attribute("SeriesNumber", "1")
    sc_image.add_pixel_data(data.retina(), photometric_interpretation="RGB")
    study_folder = os.path.join(output_folder, "data", "sc_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_no_tiling"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "retina_no_tiling", 
                                str(sc_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    sc_image.write_to_file(output_file)

if __name__ == "__main__":
    run()