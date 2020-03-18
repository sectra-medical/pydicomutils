import os
import glob
from shutil import copy
from datetime import datetime
import numpy as np
from pydicom import read_file
from pydicomutils.IODs.EnhancedSRTID1500 import EnhancedSRTID1500

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # find original images
    input_folder = os.path.join(file_folder, "data", "ct_images", "original_dicom_images")
    referenced_dcm_files = glob.glob(os.path.join(input_folder,"*.dcm"))

    # set output folder
    output_folder = os.path.join(output_folder, "data", "ct_images", "linear_measurements")

    # copy original images to output folder
    ds = read_file(referenced_dcm_files[0])
    dcm_folder = os.path.join(output_folder, "series_" + str(ds.SeriesNumber))
    os.makedirs(dcm_folder, exist_ok=True)
    for dcm_file in referenced_dcm_files:
        copy(dcm_file, dcm_folder)

    # create dict of dicom objects
    sop_instance_uid_to_dcm_file = dict()
    for dcm_file in referenced_dcm_files:
        ds = read_file(dcm_file)
        sop_instance_uid_to_dcm_file[ds.SOPInstanceUID] = dcm_file

    # create enhaned SR objects according to TID 1500 with linear measurements    
    enhanced_sr = EnhancedSRTID1500()
    enhanced_sr.create_empty_iod()
    enhanced_sr.initiate(referenced_dcm_files)
    enhanced_sr.set_dicom_attribute("Manufacturer", "Company Inc.")
    enhanced_sr.set_dicom_attribute("SeriesNumber", "400")
    enhanced_sr.set_dicom_attribute("SeriesDescription", "Imaging Measurement Report")
    enhanced_sr.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
    enhanced_sr.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
    enhanced_sr.add_linear_measurement_double_axis(sop_instance_uid_to_dcm_file["1.3.6.1.4.1.14519.5.2.1.6279.6001.824843590991776411530080688091"],
        32.2, [299, 343, 326, 380], ["103339001", "SCT", "Long Axis"],
        23.1, [302, 380, 328, 361], ["103340004", "SCT", "Short Axis"],
        ["5298800", "SCT", "Lesion"],
        ["39607008", "SCT", "Lung"],
        coded_values=[{"ConceptNameCode": ["31094006","SCT", "Lobe of lung"],
                    "ConceptCode": ["41224006", "SCT", "Lower lobe of left lung"]},
                    {"ConceptNameCode": ["RID6037","RADLEX", "Attenuation Characteristic"],
                    "ConceptCode": ["RID5741", "RADLEX", "Solid"]},
                    {"ConceptNameCode": ["129737002","SCT", "Radiographic lesion margin"],
                    "ConceptCode": ["129742005", "SCT", "Lesion with spiculated margin"]}])

    os.makedirs(os.path.join(output_folder,
                            "series_" + str(enhanced_sr.dataset.SeriesNumber).zfill(3)), 
                            exist_ok=True)
    output_file = os.path.join(output_folder,
                            "series_" + str(enhanced_sr.dataset.SeriesNumber).zfill(3), 
                            "sr.dcm")
    enhanced_sr.write_to_file(output_file)