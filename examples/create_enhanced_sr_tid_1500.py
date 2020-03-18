import os
import glob
import pandas
from datetime import datetime
from pydicomutils.IODs.EnhancedSRTID1500 import EnhancedSRTID1500

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    df_data_entries = pandas.read_csv(os.path.join(file_folder, "data", "cr_images", "Data_Entry_2017.csv"))
    df_bbox_entries = pandas.read_csv(os.path.join(file_folder, "data", "cr_images", "BBox_List_2017.csv"))
    df_data_entries.set_index("ImageIndex")
    df_data_entries.sort_values(by="ImageIndex")
    patient_ids = df_data_entries["PatientID"].unique()

    for patient_id in patient_ids[0:1]:
        patient_df = df_data_entries[df_data_entries["PatientID"] == patient_id]
        study_ids = patient_df["FollowUp"].unique()
        for study_id in study_ids[0:1]:
            study_df = patient_df[patient_df["FollowUp"] == study_id]
            study_id = str(patient_id).zfill(6) + str(study_id).zfill(4)
            study_folder = os.path.join(output_folder, "data", "cr_images", "output", study_id)
            referenced_dcm_files = glob.glob(os.path.join(study_folder,"series_001","*.dcm"))

            # Create Enhanced SR TID 1500 adding a guessed clavicle location
            enhanced_sr = EnhancedSRTID1500()
            enhanced_sr.create_empty_iod()
            enhanced_sr.initiate(referenced_dcm_files)
            enhanced_sr.set_dicom_attribute("SeriesNumber", "350")
            enhanced_sr.set_dicom_attribute("SeriesDescription", "Landmarks")
            enhanced_sr.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
            enhanced_sr.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
            enhanced_sr.add_landmark(referenced_dcm_files[0], 
                [240, 200], ["51299004", "SCT", "Clavicle"], ["51185008", "SCT", "Chest"])

            os.makedirs(os.path.join(study_folder,
                                    "series_" + str(enhanced_sr.dataset.SeriesNumber).zfill(3)), 
                                    exist_ok=True)
            output_file = os.path.join(study_folder,
                                    "series_" + str(enhanced_sr.dataset.SeriesNumber).zfill(3), 
                                    "sr.dcm")
            enhanced_sr.write_to_file(output_file)
