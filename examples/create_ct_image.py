import os
import numpy as np
import SimpleITK as sitk
import random
from datetime import datetime
from pydicom import uid
from pydicomutils.IODs.CTImage import CTImage

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # set output folder
    study_folder = os.path.join(output_folder, "data", "ct_images", "converted_images")
    os.makedirs(study_folder, exist_ok=True)

    # original file to convert
    original_image_file = os.path.join(file_folder, "data", "ct_images", "non_dicom", "LIDC-IDRI-0001_CT.nrrd")

    # load data from image file
    img = sitk.ReadImage(original_image_file)
    arr = sitk.GetArrayFromImage(img)
    arr = np.swapaxes(arr, 0, 1)
    arr = np.swapaxes(arr, 1, 2)

    # get orientation and position vectors
    img_position = img.GetOrigin()
    img_orientation = img.GetDirection()

    # set reusable metadata
    patient_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    study_instance_uid = uid.generate_uid()
    study_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    accession_number = study_id
    study_date = datetime.now().strftime("%Y%m%d")
    study_time = datetime.now().strftime("%H%M%S")
    series_instance_uid = uid.generate_uid()
    series_number = "100"
    series_date = datetime.now().strftime("%Y%m%d")
    series_time = datetime.now().strftime("%H%M%S")
    frame_of_reference_uid = uid.generate_uid()
    study_description = "CT PELVIS"
    series_description = "Axial"
    body_part_examined = "PELVIS"
    patient_position = ""

    # initiate metadata on instance level
    instance_no = 0
    for slice_ind in range(0, img.GetSize()[2]):
        instance_no += 1
        ct_image = CTImage()
        ct_image.create_empty_iod()
        ct_image.initiate()
        ct_image.set_dicom_attribute("PatientID", patient_id)
        ct_image.set_dicom_attribute("StudyInstanceUID", study_instance_uid)
        ct_image.set_dicom_attribute("StudyID", study_id)
        ct_image.set_dicom_attribute("AccessionNumber", accession_number)
        ct_image.set_dicom_attribute("StudyDate", study_date)
        ct_image.set_dicom_attribute("StudyTime", study_time)
        ct_image.set_dicom_attribute("SeriesInstanceUID", series_instance_uid)
        ct_image.set_dicom_attribute("SeriesNumber", series_number)
        ct_image.set_dicom_attribute("SeriesDate", series_date)
        ct_image.set_dicom_attribute("SeriesTime", series_time)
        ct_image.set_dicom_attribute("FrameOfReferenceUID", frame_of_reference_uid)
        ct_image.set_dicom_attribute("StudyDescription", study_description)
        ct_image.set_dicom_attribute("SeriesDescription", series_description)
        ct_image.set_dicom_attribute("BodyPartExamined", body_part_examined)
        ct_image.set_dicom_attribute("PatientPosition", patient_position)
        ct_image.set_dicom_attribute("ContentDate", datetime.now().strftime("%Y%m%d"))
        ct_image.set_dicom_attribute("ContentTime", datetime.now().strftime("%H%M%S"))
        ct_image.set_dicom_attribute("InstanceNumber", str(instance_no))
        ct_image.set_dicom_attribute("ImageOrientationPatient", 
                                     [str(img_orientation[0])[:16], str(img_orientation[1])[:16], str(img_orientation[2])[:16],
                                      str(img_orientation[3])[:16], str(img_orientation[4])[:16], str(img_orientation[5])[:16]])
        ct_image.set_dicom_attribute("ImagePositionPatient", 
                                    [str(img_position[0] + slice_ind*img_orientation[6])[:16],
                                     str(img_position[1] + slice_ind*img_orientation[7])[:16],
                                     str(img_position[2] + slice_ind*img_orientation[8])[:16]])
        ct_image.set_dicom_attribute("SliceThickness", str(img.GetSpacing()[2]))
        ct_image.add_pixel_data(np.array(arr[:,:,slice_ind] + 1024, dtype=np.uint16),
                                pixel_spacing=[str(img.GetSpacing()[0])[:16],
                                            str(img.GetSpacing()[1])[:16]])
        os.makedirs(os.path.join(study_folder,"series_" + str(ct_image.dataset.SeriesNumber).zfill(3)), exist_ok=True)
        output_file = os.path.join(study_folder,
                                   "series_" + str(ct_image.dataset.SeriesNumber).zfill(3), 
                                   str(ct_image.dataset.InstanceNumber).zfill(6) + ".dcm")
        ct_image.write_to_file(output_file)