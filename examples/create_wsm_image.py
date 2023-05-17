import os
import random
import logging
from datetime import datetime
from math import pow

import requests
import numpy as np
from skimage.transform import resize
from skimage import data
from imageio import imread
from pydicom.uid import generate_uid

from pydicomutils.IODs.WSMImage import WSMImage

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

    # Simple example with BW noise
    logger.info("Simple 256x256 example with noice")
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWNoise^256x256")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "noise_256x256"), exist_ok=True)
    output_file = os.path.join(
        study_folder,
        "noise_256x256",
        str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm",
    )
    wsm_image.write_to_file(output_file)

    # Simple example with a BW test image from skimage
    logger.info("Simple 512x512 example from skimage")
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWBrick^512x512")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.brick())
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "brick_512x512"), exist_ok=True)
    output_file = os.path.join(
        study_folder,
        "brick_512x512",
        str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm",
    )
    wsm_image.write_to_file(output_file)

    # Simple example with a BW test image from skimage but with tiling
    logger.info("Simple 512x512 example from skimage with tiling")
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWBrick^WithTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.brick(), tile_size=[256, 256])
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(
        os.path.join(study_folder, "brick_512x512_tiling_256x256"), exist_ok=True
    )
    output_file = os.path.join(
        study_folder,
        "brick_512x512_tiling_256x256",
        str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm",
    )
    wsm_image.write_to_file(output_file)

    # Simple example with an RGB  test image from skimage
    logger.info("RGB example from skimage")
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "RGBRetina^NoTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(
        data.retina()[0:1410, 0:1410, :], photometric_interpretation="RGB"
    )
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_no_tiling"), exist_ok=True)
    output_file = os.path.join(
        study_folder,
        "retina_no_tiling",
        str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm",
    )
    wsm_image.write_to_file(output_file)

    # Simple example with an RGB  test image from skimage but with tiling
    logger.info("RGB example from skimage with tiling")
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "RGBRetina^WithTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(
        data.retina()[0:1410, 0:1410, :],
        photometric_interpretation="RGB",
        tile_size=[256, 256],
    )
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_tiling_256x256"), exist_ok=True)
    output_file = os.path.join(
        study_folder,
        "retina_tiling_256x256",
        str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm",
    )
    wsm_image.write_to_file(output_file)

    # Simple example with an acutal WSI image with tiling and multi-resolution
    logger.info(
        "High resolution RGB example from pexels with tiling and multi-resolution"
    )
    input_file = os.path.join(
        file_folder, "data", "wsi_images", "image_to_encode_as_dicom.jpg"
    )
    if not os.path.exists(input_file):
        logger.info("Data not available locally, downloading")
        url = "https://images.pexels.com/photos/1270184/pexels-photo-1270184.jpeg"
        downloaded_file = requests.get(url)
        open(input_file, "wb").write(downloaded_file.content)
    im = imread(input_file)
    im = im[:, :, 0:3]
    study_folder = os.path.join(output_folder, "data", "wsm_images", "BW-skull")
    os.makedirs(study_folder, exist_ok=True)
    patient_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
    accession_number = "".join(random.choice("0123456789ABCDEF") for i in range(16))
    study_instance_uid = generate_uid()
    series_instance_uid = generate_uid()
    frame_of_reference_uid = generate_uid()
    study_date = datetime.now().strftime("%Y%m%d")
    study_time = datetime.now().strftime("%H%M%S")
    for level in range(0, 3):
        logger.info("Level: " + str(level))
        wsm_image = WSMImage()
        wsm_image.create_empty_iod()
        wsm_image.initiate()
        wsm_image.set_dicom_attribute("PatientName", "Black-White^Skull")
        wsm_image.set_dicom_attribute("PatientID", patient_id)
        wsm_image.set_dicom_attribute("StudyInstanceUID", study_instance_uid)
        wsm_image.set_dicom_attribute("AccessionNumber", accession_number)
        wsm_image.set_dicom_attribute("StudyID", accession_number)
        wsm_image.set_dicom_attribute("StudyDate", study_date)
        wsm_image.set_dicom_attribute("StudyTime", study_time)
        wsm_image.set_dicom_attribute("SeriesInstanceUID", series_instance_uid)
        wsm_image.set_dicom_attribute("FrameOfReferenceUID", frame_of_reference_uid)
        wsm_image.set_dicom_attribute("SeriesNumber", "1")
        wsm_image.set_dicom_attribute("SeriesDate", study_date)
        wsm_image.set_dicom_attribute("SeriesTime", study_time)
        wsm_image.set_dicom_attribute("InstanceNumber", str(level))
        if level > 0:
            wsm_image.set_dicom_attribute(
                "ImageType", ["DERIVED", "PRIMARY", "VOLUME", "RESAMPLED"]
            )
        im_resized = resize(
            im,
            (int(im.shape[0] / pow(2, level)), int(im.shape[1] / pow(2, level)), 3),
            preserve_range=True,
        ).astype(np.uint8)
        wsm_image.add_pixel_data(
            im_resized,
            photometric_interpretation="RGB",
            pixel_spacing=[0.0005 * int(pow(2, level)), 0.0005 * int(pow(2, level))],
            tile_size=[256, 256],
        )
        output_file = os.path.join(
            study_folder, str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm"
        )
        wsm_image.write_to_file(output_file)


if __name__ == "__main__":
    run()
