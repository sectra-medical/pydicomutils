import os
import random
import pydicom
import datetime
from pydicomutils.IODs.CSPS import CSPS

def verify_presentation_state_content(presentation_state):
    """Helper function to verify that the content in presentation_state is appropriate 
    to create a basic text SR object
    ----------
    Parameters
    """
    if not isinstance(presentation_state, dict):
        print("instance is expected to be a dict")
        return

    if "SOPClassUID" not in presentation_state:
        presentation_state["SOPClassUID"] = "1.2.840.10008.5.1.4.1.1.11.2"
    if "SOPInstanceUID" not in presentation_state:
        presentation_state["SOPInstanceUID"] = pydicom.uid.generate_uid()
    if "InstanceNumber" not in presentation_state:
        presentation_state["InstanceNumber"] = "1"
    if "ContentDescription" not in presentation_state:
        presentation_state["ContentDescription"] = ""
    if "ContentCreatorName" not in presentation_state:
        presentation_state["ContentCreatorName"] = ""
    if "PresentationCreationDate" not in presentation_state:
        presentation_state["PresentationCreationDate"] = datetime.datetime.now().strftime("%Y%m%d")
    if "PresentationCreationTime" not in presentation_state:
        presentation_state["PresentationCreationTime"] = datetime.datetime.now().strftime("%H%M%S")
    return presentation_state

def verify_series_content(series):
    """Helper function to verify that the content in series is appropriate 
    to create a basic text SR object
    Parameters
    ----------
    series : A dictionary structure containing relevant DICOM
             attributes and values to create a basic text SR object
             {"Modality" : ???,
              "SeriesInstanceUID" : ???}
    """
    if not isinstance(series, dict):
        print("series is expected to be a dict")
        return
    if "Modality" not in series:
        series["Modality"] = "PR"
    if "SeriesInstanceUID" not in series:
        series["SeriesInstanceUID"] = pydicom.uid.generate_uid()

    return series

def verify_study_content(study):
    """Helper function to verify that the content in study is appropriate 
    to create a basic text SR object
    Parameters
    ----------
    """
    if not isinstance(study, dict):
        print("study is expected to be a dict")
        return
    if "PatientID" not in study:
        study["PatientID"] = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    if "StudyInstanceUID" not in study:
        study["StudyInstanceUID"] = pydicom.uid.generate_uid()
    if "StudyID" not in study or "AccessionNumber" not in study:
        study["StudyID"] = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        study["AccessionNumber"] = study["StudyID"]
    if "Manufacturer" not in study:
        study["Manufacturer"] = "UNKNOWN"
    study["series_content"] = verify_series_content(study["series_content"])
    study["presentation_state_content"] = verify_presentation_state_content(study["presentation_state_content"])

    return study
def create_csps_with_annotations(study, output_folder):
    """Helper function to create a CSPS object for a single series
    of DICOM objects
    Parameters
    ----------
    study : A nested dictionary structure containing relevant DICOM
            attributes and values to create CR images
            {"PatientID" : ???,
             "StudyInstanceUID" : ???,
             "series_content" : {
                 "Modality" : ???,
                 "SeriesInstanceUID" : ???,
                 "SeriesNumber" : ???,
                 "PresentationLUTShape" : ???
             },
             "presentation_state_content" {
                 "ContentLabel" : ???,
                 "ReferencedSeriesSequence" : [{
                     "SeriesInstanceUID" : ???,
                     "ReferencedImageSequence" : [{
                         "ReferencedSOPClassUID" : ???,
                         "ReferencedSOPInstanceUID" : ???
                     }]      
                 }],
                 "GraphicAnnotationSequence" : [{
                     "ReferencedImageSequence" : ???,
                     "GaphicLayer" : ???,
                     "TextObjectSequence" : [{
                         "AnchorPointAnnotationUnits" : ???,
                         "UnformattedTextValue" : ???,
                         "AnchorPoint"
                     }],
                     "GraphicObjectSequence" : [{
                         "GraphicAnnotationUnits" : ???,
                         "GraphicDimensions" : ???,
                         "NumberOfGraphicPoints" : ???,
                         "GraphicData" : ???,
                         "GraphicType" : ???
                     }]
                 }],
                 "GraphicLayerSequence" : [{
                     "GraphicLayer" : ???,
                     "GraphicLayerOder" : ???
                 }]
             }
            }
    output_folder : Folder to place the resulting DICOM objects in
    """
    # Verify that required values are available, otherwise, they need to be
    # be created
    study = verify_study_content(study)

    csps = CSPS()
    csps.create_empty_iod()
    
    for dicom_attribute in study.keys():
        if dicom_attribute == "series_content" or dicom_attribute == "presentation_state_content":
            continue
        csps.set_dicom_attribute(dicom_attribute, study[dicom_attribute])
    
    for dicom_attribute in study["series_content"].keys():
        csps.set_dicom_attribute(dicom_attribute, 
                                          study["series_content"][dicom_attribute])
    
    for dicom_attribute in study["presentation_state_content"].keys():
        csps.set_dicom_attribute(dicom_attribute, 
                                          study["presentation_state_content"][dicom_attribute])

    os.makedirs(os.path.join(output_folder,
                             "series_" + study["series_content"]["SeriesNumber"].zfill(3)), 
                             exist_ok=True)
    output_file = os.path.join(output_folder,
                               "series_" + study["series_content"]["SeriesNumber"].zfill(3), 
                               "pr.dcm")

    csps.write_to_file(output_file, write_like_original=False)