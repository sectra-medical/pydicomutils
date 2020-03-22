import os
import random
from datetime import datetime
from math import pow
import numpy as np
from skimage.transform import resize
from skimage import data
from imageio import imread

from pydicom.uid import generate_uid

from pydicomutils.IODs.WSMImage import WSMImage

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Dummy example with BW noise
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWNoise^256x256")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "noise_256x256"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "noise_256x256", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)

    # Dummy example with a BW test image from skimage
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWBrick^512x512")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.brick())
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "brick_512x512"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "brick_512x512", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)

    # Dummy example with a BW test image from skimage but with tiling
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "BWBrick^WithTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.brick(), tile_size=[256, 256])
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "brick_512x512_tiling_256x256"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "brick_512x512_tiling_256x256", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)

    # Dummy example with an RGB  test image from skimage
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "RGBRetina^NoTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.retina()[0:1410,0:1410,:], photometric_interpretation="RGB")
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_no_tiling"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "retina_no_tiling", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)

    # Dummy example with an RGB  test image from skimage but with tiling
    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "RGBRetina^WithTiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.retina()[0:1410,0:1410,:], photometric_interpretation="RGB", tile_size=[256, 256])
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_tiling_256x256"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "retina_tiling_256x256", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)

    # Dummy example with an acutal WSI image with tiling and multi-resolution
    input_file = os.path.join(file_folder, "data", "wsi_images", "openslide", "CMU-1-Small-Region.png")
    im = imread(input_file)
    im = im[:,:,0:3]
    study_folder = os.path.join(output_folder, "data", "wsm_images", "cmu-1-small-region-tiling-multi-res")
    os.makedirs(study_folder, exist_ok=True)
    patient_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    accession_number = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    study_instance_uid = generate_uid()
    series_instance_uid = generate_uid()
    frame_of_reference_uid = generate_uid()
    study_date = datetime.now().strftime("%Y%m%d")
    study_time = datetime.now().strftime("%H%M%S")
    for level in range(0,3):
        wsm_image = WSMImage()
        wsm_image.create_empty_iod()
        wsm_image.initiate()
        wsm_image.set_dicom_attribute("PatientName", "CMU-1^Small-Region")
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
        im_resized = resize(im, (int(im.shape[0]/pow(2, level)), int(im.shape[1]/pow(2, level)), 3), preserve_range=True).astype(np.uint8)
        wsm_image.add_pixel_data(im_resized, photometric_interpretation="RGB", pixel_spacing=[0.0005*int(pow(2, level)), 0.0005*int(pow(2, level))], tile_size=[256, 256])
        output_file = os.path.join(study_folder, str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
        wsm_image.write_to_file(output_file)

