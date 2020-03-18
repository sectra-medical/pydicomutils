import os
import glob
import pandas
from datetime import datetime
import imageio
from pydicomutils.IODs.CRImage import CRImage
from pydicomutils.IODs.GSPS import GSPS
from pydicomutils.IODs.BasicSRText import BasicSRText

def create_points_for_rectangle(x, y, width, height):
    """Simple helper function to create points for a rectangle
    
    Arguments:
        x {int} -- [description]
        y {int} -- [description]
        width {int} -- [description]
        height {int} -- [description]
    
    Returns:
        [int] -- [description]
    """
    points = []
    points.append(x)
    points.append(y)
    points.append(x)
    points.append(y + height)
    points.append(x + width)
    points.append(y + height)
    points.append(x + width)
    points.append(y)
    points.append(x)
    points.append(y)
    
    return points

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    df_data_entries = pandas.read_csv(os.path.join(file_folder, "data", "cr_images", "Data_Entry_2017.csv"))
    df_bbox_entries = pandas.read_csv(os.path.join(file_folder, "data", "cr_images", "BBox_List_2017.csv"))
    df_data_entries.set_index("ImageIndex")
    df_data_entries.sort_values(by="ImageIndex")
    patient_ids = df_data_entries["PatientID"].unique()

    for patient_id in patient_ids:
        patient_df = df_data_entries[df_data_entries["PatientID"] == patient_id]
        study_ids = patient_df["FollowUp"].unique()
        for study_id in study_ids:
            study_df = patient_df[patient_df["FollowUp"] == study_id]

            # Create CR image
            cr_image = CRImage()
            cr_image.create_empty_iod()
            cr_image.initiate()
            cr_image.set_dicom_attribute("PatientID", "NIHCRChest" + str(patient_id).zfill(6))
            cr_image.set_dicom_attribute("PatientSex", study_df.iloc[0]["PatientSex"])
            cr_image.set_dicom_attribute("StudyID", str(patient_id).zfill(6) + str(study_id).zfill(4))
            cr_image.set_dicom_attribute("AccessionNumber", str(patient_id).zfill(6) + str(study_id).zfill(4))
            cr_image.set_dicom_attribute("StudyDescription", "Chest CR")
            cr_image.set_dicom_attribute("StudyDate", datetime.now().strftime("%Y%m%d"))
            cr_image.set_dicom_attribute("StudyTime", datetime.now().strftime("%H%M%S"))
            cr_image.set_dicom_attribute("SeriesNumber", "1")
            cr_image.set_dicom_attribute("SeriesDescription", study_df.iloc[0]["ViewPosition"])
            cr_image.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
            cr_image.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
            cr_image.set_dicom_attribute("BodyPartExamined", "CHEST")
            cr_image.set_dicom_attribute("ViewPosition", study_df.iloc[0]["ViewPosition"])
            cr_image.set_dicom_attribute("PixelSpacing", [str(study_df.iloc[0]["OriginalImagePixelSpacingX"] / (1024.0/study_df.iloc[0]["OriginalImageWidth"])),
                                                        str(study_df.iloc[0]["OriginalImagePixelSpacingY"] / (1024.0/study_df.iloc[0]["OriginalImageHeight"]))])
            cr_image.set_dicom_attribute("ImageType", ["DERIVED", "SECONDARY"])
            cr_image.add_pixel_data(imageio.imread(os.path.join(file_folder, "data", "cr_images", "images", study_df.iloc[0]["ImageIndex"])))
            
            study_folder = os.path.join(output_folder, "data", "cr_images", "output", cr_image.dataset.StudyID)
            os.makedirs(study_folder, exist_ok=True)
            available_dcm_files = glob.glob(os.path.join(study_folder, "**", "*.dcm"), recursive=True)
            for dcm_file in available_dcm_files:
                os.remove(dcm_file)
            os.makedirs(os.path.join(study_folder,"series_" + str(cr_image.dataset.SeriesNumber).zfill(3)), exist_ok=True)
            output_file = os.path.join(study_folder,
                                        "series_" + str(cr_image.dataset.SeriesNumber).zfill(3), 
                                        str(cr_image.dataset.InstanceNumber).zfill(6) + ".dcm")
            cr_image.write_to_file(output_file)

            referenced_dcm_files = glob.glob(os.path.join(study_folder,"**","*.dcm"), recursive=True)

            # Create Basic Text SR
            basic_text_sr = BasicSRText()
            basic_text_sr.create_empty_iod()
            basic_text_sr.initiate(referenced_dcm_files=referenced_dcm_files)
            basic_text_sr.set_dicom_attribute("SeriesNumber", "300")
            basic_text_sr.set_dicom_attribute("SeriesDescription", "SR Report")
            basic_text_sr.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
            basic_text_sr.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
            basic_text_sr.add_text_node(study_df.iloc[0]["FindingLabels"], ["59776-5", "LN", "Findings"])
            os.makedirs(os.path.join(study_folder,
                                    "series_" + str(basic_text_sr.dataset.SeriesNumber).zfill(3)), 
                                    exist_ok=True)
            output_file = os.path.join(study_folder,
                                    "series_" + str(basic_text_sr.dataset.SeriesNumber).zfill(3), 
                                    "sr.dcm")
            basic_text_sr.write_to_file(output_file)
            
            # Create GSPS
            if study_df.iloc[0]["ImageIndex"] in df_bbox_entries["ImageIndex"].unique():
                bbox_df = df_bbox_entries[df_bbox_entries["ImageIndex"] == study_df.iloc[0]["ImageIndex"]]
                bbox_x = bbox_df.iloc[0]["BBoxX"]
                bbox_y = bbox_df.iloc[0]["BBoxY"]
                bbox_width = bbox_df.iloc[0]["BBoxW"]
                bbox_height = bbox_df.iloc[0]["BBoxH"]

                gsps = GSPS()
                gsps.create_empty_iod()
                gsps.initiate(referenced_dcm_files=referenced_dcm_files)
                gsps.set_dicom_attribute("SeriesNumber", "500")
                gsps.set_dicom_attribute("SeriesDescription", "Finding and bounding box")
                gsps.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
                gsps.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
                gsps.set_dicom_attribute("ContentLabel", "FINDINGANDBBOX")
                gsps.add_graphical_layer("FINDINGANDBBOX", 1)
                gsps.add_text_object(referenced_dcm_files[0], "FINDINGANDBBOX", bbox_df.iloc[0]["FindingLabel"], 
                                    [float(bbox_x + bbox_width / 2.0), float(bbox_y + bbox_height / 2.0)])   
                gsps.add_graphic_object(referenced_dcm_files[0], "FINDINGANDBBOX", 
                                        create_points_for_rectangle(bbox_x, bbox_y, bbox_width, bbox_height), "POLYLINE")
                
                os.makedirs(os.path.join(study_folder,
                                        "series_" + str(gsps.dataset.SeriesNumber).zfill(3)), 
                                        exist_ok=True)
                output_file = os.path.join(study_folder,
                                            "series_" + str(gsps.dataset.SeriesNumber).zfill(3), 
                                            "pr.dcm")
                gsps.write_to_file(output_file, write_like_original=False)