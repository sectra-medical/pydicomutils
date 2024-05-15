import os
import glob
import logging
from datetime import datetime
import math

import pandas
import imageio

from pydicomutils.IODs.CRImage import CRImage
from pydicomutils.IODs.GSPS import GSPS
from pydicomutils.IODs.BasicSRText import BasicSRText
from pydicomutils.IODs.Comprehensive3DSRTID1500 import (
    Comprehensive3DSRTID1500,
    ConceptCodeSequenceItem,
    ConceptNameCodeSequenceItem,
)

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


def create_corner_points_for_rectangle_from_xywidthheight(x, y, width, height):
    """Simple helper function to create corner points for a rectangle given the top left corner and width and height"""
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


def create_center_point_from_xywidthheight(x, y, width, height):
    """Simple helper function to create center point for a rectangle given the top left corner and width and height"""
    points = []
    # Center point
    points.append(x + width / 2.0)
    points.append(y + height / 2.0)

    return points


def create_circle_points_from_xywidthheight(x, y, width, height):
    """Simple helper function to create a circle enclosing a rectangle given the top left corner and width and height"""
    points = []
    # Center point
    points.append(x + width / 2.0)
    points.append(y + height / 2.0)
    # Point on the circle
    points.append(x + width)
    points.append(y + height)

    return points


def create_octagon_points_from_xywidthheight(x, y, width, height):
    """Simple helper function to create an octagon enclosed by a rectangle given the top left corner and width and height"""
    # Calculate the center of the bounding box
    cx = x + width / 2
    cy = y + height / 2

    # Calculate the radius of the circumscribed circle
    # The radius should be such that the octagon fits within the bounding box
    radius = min(width, height) / (2 * math.sin(math.pi / 8))

    # Calculate the angle between each vertex
    angle_step = 2 * math.pi / 8

    # Generate the vertices of the octagon
    vertices = []
    for i in range(8):
        angle = angle_step * i
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        vertices.append(px)
        vertices.append(py)

    return vertices


def run():
    logger.info("Starting")
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    df_data_entries = pandas.read_csv(
        os.path.join(file_folder, "data", "cr_images", "Data_Entry_2017.csv")
    )
    df_bbox_entries = pandas.read_csv(
        os.path.join(file_folder, "data", "cr_images", "BBox_List_2017.csv")
    )
    df_data_entries.set_index("ImageIndex")
    df_data_entries.sort_values(by="ImageIndex")
    patient_ids = df_data_entries["PatientID"].unique()

    for patient_id in patient_ids:
        logger.info("Processing patient: " + str(patient_id))
        patient_df = df_data_entries[df_data_entries["PatientID"] == patient_id]
        study_ids = patient_df["FollowUp"].unique()
        for study_id in study_ids:
            logger.info("Study: " + str(study_id))
            study_df = patient_df[patient_df["FollowUp"] == study_id]

            # Create CR image
            logger.info("CR")
            cr_image = CRImage()
            cr_image.create_empty_iod()
            cr_image.initiate()
            cr_image.set_dicom_attribute(
                "PatientID", "NIHCRChest" + str(patient_id).zfill(6)
            )
            cr_image.set_dicom_attribute("PatientSex", study_df.iloc[0]["PatientSex"])
            cr_image.set_dicom_attribute(
                "StudyID", str(patient_id).zfill(6) + str(study_id).zfill(4)
            )
            cr_image.set_dicom_attribute(
                "AccessionNumber", str(patient_id).zfill(6) + str(study_id).zfill(4)
            )
            cr_image.set_dicom_attribute("StudyDescription", "Chest CR")
            cr_image.set_dicom_attribute("StudyDate", datetime.now().strftime("%Y%m%d"))
            cr_image.set_dicom_attribute("StudyTime", datetime.now().strftime("%H%M%S"))
            cr_image.set_dicom_attribute("SeriesNumber", "1")
            cr_image.set_dicom_attribute(
                "SeriesDescription", study_df.iloc[0]["ViewPosition"]
            )
            cr_image.set_dicom_attribute(
                "SeriesDate", datetime.now().strftime("%Y%m%d")
            )
            cr_image.set_dicom_attribute(
                "SeriesTime", datetime.now().strftime("%H%M%S")
            )
            cr_image.set_dicom_attribute("BodyPartExamined", "CHEST")
            cr_image.set_dicom_attribute(
                "ViewPosition", study_df.iloc[0]["ViewPosition"]
            )
            cr_image.set_dicom_attribute(
                "PixelSpacing",
                [
                    str(
                        study_df.iloc[0]["OriginalImagePixelSpacingX"]
                        / (1024.0 / study_df.iloc[0]["OriginalImageWidth"])
                    ),
                    str(
                        study_df.iloc[0]["OriginalImagePixelSpacingY"]
                        / (1024.0 / study_df.iloc[0]["OriginalImageHeight"])
                    ),
                ],
            )
            cr_image.set_dicom_attribute("ImageType", ["DERIVED", "SECONDARY"])
            cr_image.add_pixel_data(
                imageio.imread(
                    os.path.join(
                        file_folder,
                        "data",
                        "cr_images",
                        "images",
                        study_df.iloc[0]["ImageIndex"],
                    )
                )
            )

            study_folder = os.path.join(
                output_folder, "data", "cr_images", "output", cr_image.dataset.StudyID
            )
            os.makedirs(study_folder, exist_ok=True)
            available_dcm_files = glob.glob(
                os.path.join(study_folder, "**", "*.dcm"), recursive=True
            )
            for dcm_file in available_dcm_files:
                os.remove(dcm_file)
            os.makedirs(
                os.path.join(
                    study_folder,
                    "series_" + str(cr_image.dataset.SeriesNumber).zfill(3),
                ),
                exist_ok=True,
            )
            output_file = os.path.join(
                study_folder,
                "series_" + str(cr_image.dataset.SeriesNumber).zfill(3),
                str(cr_image.dataset.InstanceNumber).zfill(6) + ".dcm",
            )
            cr_image.write_to_file(output_file)

            referenced_dcm_files = glob.glob(
                os.path.join(study_folder, "**", "*.dcm"), recursive=True
            )

            # Create Basic Text SR
            logger.info("Basic Text SR")
            basic_text_sr = BasicSRText()
            basic_text_sr.create_empty_iod()
            basic_text_sr.initiate(referenced_dcm_files=referenced_dcm_files)
            basic_text_sr.set_dicom_attribute("SeriesNumber", "300")
            basic_text_sr.set_dicom_attribute(
                "SeriesDescription", "Basic Text SR Report"
            )
            basic_text_sr.set_dicom_attribute(
                "SeriesDate", datetime.now().strftime("%Y%m%d")
            )
            basic_text_sr.set_dicom_attribute(
                "SeriesTime", datetime.now().strftime("%H%M%S")
            )
            basic_text_sr.add_text_node(
                study_df.iloc[0]["FindingLabels"], ["59776-5", "LN", "Findings"]
            )
            os.makedirs(
                os.path.join(
                    study_folder,
                    "series_" + str(basic_text_sr.dataset.SeriesNumber).zfill(3),
                ),
                exist_ok=True,
            )
            output_file = os.path.join(
                study_folder,
                "series_" + str(basic_text_sr.dataset.SeriesNumber).zfill(3),
                "sr.dcm",
            )
            basic_text_sr.write_to_file(output_file)

            # Create GSPS and Comprehensive 3D SR TID 1500
            if study_df.iloc[0]["ImageIndex"] in df_bbox_entries["ImageIndex"].unique():
                logger.info("GSPS")
                bbox_df = df_bbox_entries[
                    df_bbox_entries["ImageIndex"] == study_df.iloc[0]["ImageIndex"]
                ]
                bbox_x = bbox_df.iloc[0]["BBoxX"]
                bbox_y = bbox_df.iloc[0]["BBoxY"]
                bbox_width = bbox_df.iloc[0]["BBoxW"]
                bbox_height = bbox_df.iloc[0]["BBoxH"]

                gsps = GSPS()
                gsps.create_empty_iod()
                gsps.initiate(referenced_dcm_files=referenced_dcm_files)
                gsps.set_dicom_attribute("SeriesNumber", "500")
                gsps.set_dicom_attribute(
                    "SeriesDescription", "Finding and bounding box"
                )
                gsps.set_dicom_attribute(
                    "SeriesDate", datetime.now().strftime("%Y%m%d")
                )
                gsps.set_dicom_attribute(
                    "SeriesTime", datetime.now().strftime("%H%M%S")
                )
                gsps.set_dicom_attribute("ContentLabel", "FINDINGANDBBOX")
                gsps.add_graphical_layer("FINDINGANDBBOX", 1)
                gsps.add_text_object(
                    referenced_dcm_files[0],
                    "FINDINGANDBBOX",
                    bbox_df.iloc[0]["FindingLabel"],
                    [
                        float(bbox_x + bbox_width / 2.0),
                        float(bbox_y + bbox_height / 2.0),
                    ],
                )
                gsps.add_graphic_object(
                    referenced_dcm_files[0],
                    "FINDINGANDBBOX",
                    create_corner_points_for_rectangle_from_xywidthheight(
                        bbox_x, bbox_y, bbox_width, bbox_height
                    ),
                    "POLYLINE",
                )

                os.makedirs(
                    os.path.join(
                        study_folder,
                        "series_" + str(gsps.dataset.SeriesNumber).zfill(3),
                    ),
                    exist_ok=True,
                )
                output_file = os.path.join(
                    study_folder,
                    "series_" + str(gsps.dataset.SeriesNumber).zfill(3),
                    "pr.dcm",
                )
                gsps.write_to_file(output_file, write_like_original=False)

                logger.info("Comprehensive 3D SR TID 1500")
                comprehensive_3d_sr = Comprehensive3DSRTID1500(
                    referenced_dcms=referenced_dcm_files
                )
                comprehensive_3d_sr.set_dicom_attribute("SeriesNumber", "350")
                comprehensive_3d_sr.set_dicom_attribute(
                    "SeriesDescription", "Comprehensive 3D SR TID 1500 Report"
                )
                comprehensive_3d_sr.set_dicom_attribute(
                    "SeriesDate", datetime.now().strftime("%Y%m%d")
                )
                comprehensive_3d_sr.set_dicom_attribute(
                    "SeriesTime", datetime.now().strftime("%H%M%S")
                )
                if bbox_df.iloc[0]["FindingLabel"] == "Atelectasis":
                    finding_type = ConceptCodeSequenceItem(
                        "46621007",
                        "SCT",
                        "Atelectasis",
                    )
                elif bbox_df.iloc[0]["FindingLabel"] == "Cardiomegaly":
                    finding_type = ConceptCodeSequenceItem(
                        "8186001",
                        "SCT",
                        "Cardiomegaly",
                    )
                elif bbox_df.iloc[0]["FindingLabel"] == "Pleural effusion":
                    finding_type = ConceptCodeSequenceItem(
                        "60046008",
                        "SCT",
                        "Pleural effusion",
                    )
                elif bbox_df.iloc[0]["FindingLabel"] == "Infiltrate":
                    finding_type = ConceptCodeSequenceItem(
                        "409609008",
                        "SCT",
                        "Pulmonary infiltrate",
                    )
                else:
                    finding_type = "OTHER"
                # Add finding with no location
                comprehensive_3d_sr.add_qualitative_finding(
                    referenced_dcm_files[0],
                    finding_type,
                    tracking_id="Finding",
                    finding_site=ConceptCodeSequenceItem(
                        "39607008",
                        "SCT",
                        "Lung",
                    ),
                )
                # Add finding with location as point
                comprehensive_3d_sr.add_qualitative_finding(
                    referenced_dcm_files[0],
                    finding_type,
                    tracking_id="FindingWithPoint",
                    finding_site=ConceptCodeSequenceItem(
                        "39607008",
                        "SCT",
                        "Lung",
                    ),
                    location_data=create_center_point_from_xywidthheight(
                        bbox_x, bbox_y, bbox_width, bbox_height
                    ),
                    location_type="POINT",
                )
                # Add finding with location as polyline
                comprehensive_3d_sr.add_qualitative_finding(
                    referenced_dcm_files[0],
                    finding_type,
                    tracking_id="FindingWithRectangle",
                    finding_site=ConceptCodeSequenceItem(
                        "39607008",
                        "SCT",
                        "Lung",
                    ),
                    location_data=create_corner_points_for_rectangle_from_xywidthheight(
                        bbox_x, bbox_y, bbox_width, bbox_height
                    ),
                    location_type="POLYLINE",
                )
                # Add finding with location as circle
                comprehensive_3d_sr.add_qualitative_finding(
                    referenced_dcm_files[0],
                    finding_type,
                    tracking_id="FindingWithCircle",
                    finding_site=ConceptCodeSequenceItem(
                        "39607008",
                        "SCT",
                        "Lung",
                    ),
                    location_data=create_circle_points_from_xywidthheight(
                        bbox_x, bbox_y, bbox_width, bbox_height
                    ),
                    location_type="CIRCLE",
                )
                # Add finding with region as contour
                comprehensive_3d_sr.add_qualitative_finding(
                    referenced_dcm_files[0],
                    finding_type,
                    tracking_id="FindingWithRegion",
                    finding_site=ConceptCodeSequenceItem(
                        "39607008",
                        "SCT",
                        "Lung",
                    ),
                    contour_data=create_octagon_points_from_xywidthheight(
                        bbox_x, bbox_y, bbox_width, bbox_height
                    ),
                    contour_type="POLYLINE",
                )
                # Write file to disk
                os.makedirs(
                    os.path.join(
                        study_folder,
                        "series_"
                        + str(comprehensive_3d_sr.dataset.SeriesNumber).zfill(3),
                    ),
                    exist_ok=True,
                )
                output_file = os.path.join(
                    study_folder,
                    "series_" + str(comprehensive_3d_sr.dataset.SeriesNumber).zfill(3),
                    "comprehensive3dsr.dcm",
                )
                comprehensive_3d_sr.write_to_file(
                    output_file, write_like_original=False
                )


if __name__ == "__main__":
    run()
