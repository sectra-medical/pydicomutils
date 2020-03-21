import os
import numpy as np
from skimage import data

from pydicom.uid import generate_uid

from pydicomutils.IODs.WSMImage import WSMImage

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

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

    wsm_image = WSMImage()
    wsm_image.create_empty_iod()
    wsm_image.initiate()
    wsm_image.set_dicom_attribute("PatientName", "RGBRetina^Tiling")
    wsm_image.set_dicom_attribute("SeriesNumber", "1")
    wsm_image.add_pixel_data(data.retina()[0:1410,0:1410,:], photometric_interpretation="RGB", tile_size=[256, 256])
    study_folder = os.path.join(output_folder, "data", "wsm_images")
    os.makedirs(study_folder, exist_ok=True)
    os.makedirs(os.path.join(study_folder, "retina_tiling_256x256"), exist_ok=True)
    output_file = os.path.join(study_folder,
                                 "retina_tiling_256x256", 
                                str(wsm_image.dataset.InstanceNumber).zfill(6) + ".dcm")
    wsm_image.write_to_file(output_file)