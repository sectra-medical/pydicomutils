from pydicom import Sequence, Dataset, read_file, DataElement
from pydicom.datadict import tag_for_keyword, dictionary_VM, dictionary_VR
from pydicom.uid import generate_uid


"""Various definitions that can be of good use
"""
MODALITY_CODE_MODALITY_DESCRIPION_DICT = {
    "AR": "Autorefraction",
    "ASMT": "Content Assessment Results",
    "AU": "Audio",
    "BDUS": "Bone Densitometry (ultrasound)",
    "BI": "Biomagnetic imaging",
    "BMD": "Bone Densitometry (X-Ray)",
    "CR": "Computed Radiography",
    "CT": "Computed Tomography",
    "DG": "Diaphanography",
    "DOC": "Document",
    "DX": "Digital Radiography",
    "ECG": "Electrocardiography",
    "EPS": "Cardiac Electrophysiology",
    "ES": "Endoscopy",
    "FID": "Fiducials",
    "GM": "General Microscopy",
    "HC": "Hard Copy",
    "HD": "Hemodynamic Waveform",
    "IO": "Intra-Oral Radiography",
    "IOL": "Intraocular Lens Data",
    "IVOCT": "Intravascular Optical Coherence Tomography",
    "IVUS": "Intravascular Ultrasound",
    "KER": "Keratometry",
    "KO": "Key Object Selection",
    "LEN": "Lensometry",
    "LS": "Laser surface scan",
    "MG": "Mammography",
    "MR": "Magnetic Resonance",
    "NM": "Nuclear Medicine",
    "OAM": "Ophthalmic Axial Measurements",
    "OCT": "Optical Coherence Tomography (non-Ophthalmic)",
    "OP": "Ophthalmic Photography",
    "OPM": "Ophthalmic Mapping",
    "OPT": "Ophthalmic Tomography",
    "OPV": "Ophthalmic Visual Field",
    "OSS": "Optical Surface Scan",
    "OT": "Other",
    "PLAN": "Plan",
    "PR": "Presentation State",
    "PT": "Positron emission tomography (PET)",
    "PX": "Panoramic X-Ray",
    "REG": "Registration",
    "RESP": "Respiratory Waveform",
    "RF": "Radio Fluoroscopy",
    "RG": "Radiographic imaging (conventional film/screen)",
    "RTDOSE": "Radiotherapy Dose",
    "RTIMAGE": "Radiotherapy Image",
    "RTPLAN": "Radiotherapy Plan",
    "RTRECORD": "RT Treatment Record",
    "RTSTRUCT": "Radiotherapy Structure Set",
    "RWV": "Real World Value Map",
    "SEG": "Segmentation",
    "SM": "Slide Microscopy",
    "SMR": "Stereometric Relationship",
    "SR": "SR Document",
    "SRF": "Subjective Refraction",
    "STAIN": "Automated Slide Stainer",
    "TG": "Thermography",
    "US": "Ultrasound",
    "VA": "Visual Acuity",
    "XA": "X-Ray Angiography",
    "XC": "External-camera Photography",
}


def update_and_insert_additional_DICOM_attributes_in_ds(ds, keyword_and_value_dict):
    # For every keyword
    for keyword in keyword_and_value_dict:
        # Get corresponding tag and value
        tag = tag_for_keyword(keyword)
        # Verify that it is a valid keyword
        if tag is None:
            print("Unknown DICOM attribute:", keyword)
            continue
        # Get corresponding value
        value = None
        if dictionary_VR(tag) == "SQ":
            value = generate_sequence(keyword, keyword_and_value_dict[keyword])
        else:
            value = keyword_and_value_dict[keyword]
        # If keyword already set, update its value, otherwise, create a new data element
        if keyword in ds:
            ds[tag].value = value
        else:
            ds[tag] = DataElement(tag, dictionary_VR(tag), value)
    # Return edited dataset
    return ds


def generate_reference_sop_sequence_json(dcm):
    """

    Arguments:
        dcm_file {[type]} -- [description]
    """
    ds = None
    if isinstance(dcm, Dataset):
        ds = dcm
    else:
        ds = read_file(dcm)
    return {
        "ReferencedSOPSequence": [
            {
                "ReferencedSOPClassUID": ds.SOPClassUID,
                "ReferencedSOPInstanceUID": ds.SOPInstanceUID,
            }
        ],
        "RelationshipType": "CONTAINS",
        "ValueType": "IMAGE",
        "ContentSequence": [
            {
                "RelationshipType": "HAS ACQ CONTEXT",
                "ValueType": "CODE",
                "ConceptNameCodeSequence": [
                    {
                        "CodeValue": "121139",
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": "Modality",
                    }
                ],
                "ConceptCodeSequence": [
                    {
                        "CodeValue": ds.Modality,
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": MODALITY_CODE_MODALITY_DESCRIPION_DICT[
                            ds.Modality
                        ],
                    }
                ],
            },
            {
                "RelationshipType": "HAS ACQ CONTEXT",
                "ValueType": "DATE",
                "ConceptNameCodeSequence": [
                    {
                        "CodeValue": "111060",
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": "Study Date",
                    }
                ],
                "Date": ds.StudyDate,
            },
            {
                "RelationshipType": "HAS ACQ CONTEXT",
                "ValueType": "TIME",
                "ConceptNameCodeSequence": [
                    {
                        "CodeValue": "111061",
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": "Study Time",
                    }
                ],
                "Time": ds.StudyTime,
            },
        ],
    }


def generate_DAS_sequence(dcms):
    """Helper function to generate a Displayed Area Selection Sequence
    with required DICOM attributes from a list of DICOM objects

    Arguments:
        dcms {[dcm_file1, dcm_file2, ...]} -- List of file paths

    Returns:
        Sequence -- A diplayed area selection sequence
    """
    sequence_data = [
        {
            "ReferencedImageSequence": [
                {
                    "ReferencedSOPClassUID": ds.SOPClassUID,
                    "ReferencedSOPInstanceUID": ds.SOPInstanceUID,
                }
            ],
            "DisplayedAreaTopLeftHandCorner": [1, 1],
            "DisplayedAreaBottomRightHandCorner": [int(ds.Columns), int(ds.Rows)],
            "PresentationSizeMode": "SCALE TO FIT",
        }
        for ds in [read_file(dcm_file) for dcm_file in dcms]
    ]
    return generate_sequence("DisplayedAreaSelectionSequence", sequence_data)


def generate_RS_sequence(dcms):
    """Helper function to generate a Referenced Series Sequence
    with required DICOM attributes from a list of DICOM objects

    Arguments:
        dcms {[dcm_file1, dcm_file2, ...]} -- List of file paths

    Returns:
        Sequence -- A referenced series sequence
    """
    sequence_content = dict()
    for dcm_file in dcms:
        ds = read_file(dcm_file)
        if ds.SeriesInstanceUID not in sequence_content:
            sequence_content[ds.SeriesInstanceUID] = list()
        sequence_content[ds.SeriesInstanceUID].append(
            (ds.SOPClassUID, ds.SOPInstanceUID)
        )
    sequence_data = list()
    for series_instance_uid in sequence_content:
        series_dict = dict()
        series_dict["SeriesInstanceUID"] = series_instance_uid
        series_dict["ReferencedImageSequence"] = list()
        for class_instance_uid_tuple in sequence_content[series_instance_uid]:
            instance_dict = dict()
            instance_dict["ReferencedSOPClassUID"] = class_instance_uid_tuple[0]
            instance_dict["ReferencedSOPInstanceUID"] = class_instance_uid_tuple[1]
            series_dict["ReferencedImageSequence"].append(instance_dict)
        sequence_data.append(series_dict)
    return generate_sequence("ReferencedSeriesSequence", sequence_data)


def generate_CRPES_sequence(dcms):
    """Helper function to generate a Current Requested Procedure Evidence Sequence
    with required DICOM attributes from a list of DICOM objects
    Parameters
    ----------
    dcms : List of DICOM objects that are to be referenced in the
                Current Requested Procedure Evidence Sequence
    """
    sequence_content = dict()
    for dcm in dcms:
        ds = None
        if isinstance(dcm, Dataset):
            ds = dcm
        else:
            ds = read_file(dcm)
        if ds.StudyInstanceUID not in sequence_content:
            sequence_content[ds.StudyInstanceUID] = dict()
        if ds.SeriesInstanceUID not in sequence_content[ds.StudyInstanceUID]:
            sequence_content[ds.StudyInstanceUID][ds.SeriesInstanceUID] = list()
        sequence_content[ds.StudyInstanceUID][ds.SeriesInstanceUID].append(
            (ds.SOPClassUID, ds.SOPInstanceUID)
        )
    sequence_data = list()
    for study_instance_uid in sequence_content:
        study_dict = dict()
        study_dict["StudyInstanceUID"] = study_instance_uid
        study_dict["ReferencedSeriesSequence"] = list()
        for series_instance_uid in sequence_content[study_instance_uid]:
            series_dict = dict()
            series_dict["SeriesInstanceUID"] = series_instance_uid
            series_dict["ReferencedSOPSequence"] = list()
            for class_instance_uid_tuple in sequence_content[study_instance_uid][
                series_instance_uid
            ]:
                instance_dict = dict()
                instance_dict["ReferencedSOPClassUID"] = class_instance_uid_tuple[0]
                instance_dict["ReferencedSOPInstanceUID"] = class_instance_uid_tuple[1]
                series_dict["ReferencedSOPSequence"].append(instance_dict)
            study_dict["ReferencedSeriesSequence"].append(series_dict)
        sequence_data.append(study_dict)
    sequence = Sequence()
    for study_item in sequence_data:
        study_ds = Dataset()
        study_ds.StudyInstanceUID = study_instance_uid
        study_ds.ReferencedSeriesSequence = generate_sequence(
            "ReferencedSeriesSequence", study_item["ReferencedSeriesSequence"]
        )
        sequence.append(study_ds)
    return sequence


class SequenceInternal:
    """Internal Sequence class
    Parameters
    ----------
    """

    sequence = None

    def __init__(self):
        self.sequence = Sequence()

    def get_sequence(self):
        """Get the sequence"""
        return self.sequence


class DummySequence(SequenceInternal):
    """Dummy Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.Dummy = "DEFAULT"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ConceptNameCodeSequence(SequenceInternal):
    """Concept Name Code Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.CodeMeaning = ""
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ConceptCodeSequence(SequenceInternal):
    """Concept Code Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.CodeMeaning = ""
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ContentSequence(SequenceInternal):
    """Content Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes

            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ContentTemplateSequence(SequenceInternal):
    """Content Template Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.MappingResource = ""
            ds.TemplateIdentifier = ""
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class CurrentRequestedProcedureEvidenceSequence(SequenceInternal):
    """Current Requested Procedure Evidence Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.StudyInstanceUID = ""
            ds.ReferencedSeriesSequence = generate_sequence(
                "ReferencedSeriesSequence", dict()
            )
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class PerformedProcedureCodeSequence(SequenceInternal):
    """Performed Procedure Code Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.CodeMeaning = ""
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class MeasuredValueSequence(SequenceInternal):
    """Measured Value Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.NumericValue = None
            ds.MeasurementUnitsCodeSequence = generate_sequence(
                "MeasurementUnitsCodeSequence", dict()
            )
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class MeasurementUnitsCodeSequence(SequenceInternal):
    """Measurement Units Code Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.CodeMeaning = ""
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ReferencedSeriesSequence(SequenceInternal):
    """Referenced Series Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.SeriesInstanceUID = generate_uid()
            ds.ReferencedSOPSequence = generate_sequence(
                "ReferencedSOPSequence", dict()
            )
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Remove mutually exclusive elemenets
            if (
                "ReferencedSOPSequence" in sequence_item
                and "ReferencedImageSequence" in ds
            ):
                del ds.ReferencedImageSequence
            elif (
                "ReferencedImageSequence" in sequence_item
                and "ReferencedSOPSequence" in ds
            ):
                del ds.ReferencedSOPSequence
            self.sequence.append(ds)


class ReferencedImageSequence(SequenceInternal):
    """Referenced Image Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
            ds.ReferencedSOPInstanceUID = generate_uid()
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class ReferencedSOPSequence(SequenceInternal):
    """Referenced Image Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
            ds.ReferencedSOPInstanceUID = generate_uid()
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class DisplayedAreaSelectionSequence(SequenceInternal):
    """Displayed Area Selection Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.DisplayedAreaTopLeftHandCorner = [1, 1]
            ds.DisplayedAreaBottomRightHandCorner = [100, 100]
            ds.PresentationSizeMode = "SCALE TO FIT"
            ds.PresentationPixelSpacing = ["1.0", "1.0"]
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class GraphicAnnotationSequence(SequenceInternal):
    """Graphic Annotation Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.GraphicLayer = "DEFAULT"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class TextObjectSequence(SequenceInternal):
    """Text Object Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.AnchorPointAnnotationUnits = "PIXEL"
            ds.UnformattedTextValue = "DEFAULT VALUE"
            ds.AnchorPoint = [100, 100]
            ds.AnchorPointVisibility = "N"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Remove mutually exclusive elemenets
            if "AnchorPoint" in sequence_item and "BoundingBoxTopLeftHandCorner" in ds:
                del ds.BoundingBoxTopLeftHandCorner
                del ds.BoundingBoxBottomRightHandCorner
                del ds.BoundingBoxAnnotationUnits
                del ds.BoundingBoxTextHorizontalJustification
            elif (
                "BoundingBoxTopLeftHandCorner" in sequence_item and "AnchorPoint" in ds
            ):
                del ds.AnchorPoint
                del ds.AnchorPointAnnotationUnits
                del ds.AnchorPointVisibility
            # Add dataset to sequence
            self.sequence.append(ds)


class TextStyleSequence(SequenceInternal):
    """Text Style Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.CSSFontName = "Time New Roman"
            ds.TextColorCIELabValue = [65535, 32896, 32896]  # white
            ds.ShadowStyle = "NORMAL"
            ds.ShadowOffsetX = 1.0
            ds.ShadowOffsetY = 1.0
            ds.ShadowColorCIELabValue = [0, 32896, 32896]  # black
            ds.ShadowOpacity = 1.0
            ds.Underlined = "N"
            ds.Bold = "N"
            ds.Italic = "N"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class GraphicObjectSequence(SequenceInternal):
    """Graphic Object Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.GraphicAnnotationUnits = "PIXEL"
            ds.GraphicDimensions = sequence_item["GraphicDimensions"]
            ds.NumberOfGraphicPoints = 1
            ds.GraphicData = [100, 100]
            ds.GraphicType = "POINT"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class LineStyleSequence(SequenceInternal):
    """Line Style Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.PatternOnColorCIELabValue = [65535, 32896, 32896]  # white
            ds.PatternOnOpacity = 1.0
            ds.LineThickness = 1.0
            ds.LineDashingStyle = "SOLID"
            ds.ShadowStyle = "NORMAL"
            ds.ShadowOffsetX = 1.0
            ds.ShadowOffsetY = 1.0
            ds.ShadowColorCIELabValue = [0, 32896, 32896]  # black
            ds.ShadowOpacity = 1.0
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class FillStyleSequence(SequenceInternal):
    """Fill Style Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.PatternOnColorCIELabValue = [65535, 32896, 32896]  # white
            ds.PatternOnOpacity = 1.0
            ds.FillMode = "SOLID"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class GraphicLayerSequence(SequenceInternal):
    """Graphic Layer Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.GraphicLayer = "DEFAULT"
            ds.GraphicLayerOrder = "1"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class SoftcopyVOILUTSequence(SequenceInternal):
    """Softcopy VOI LUT Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes
            ds.WindowCenter = "50"
            ds.WindowWidth = "100"
            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


class GeneralSequence(SequenceInternal):
    """General Sequence class"""

    def __init__(self, sequence_data):
        """Object initialization
        Parameters
        ----------
        sequence_data : List of items with data to generate each sequence item,
                        in the format of a list with a dictionary for each item,
                        which in turn can contain a sequence, e.g. list of dictionaries
        """
        super().__init__()
        for sequence_item in sequence_data:
            # Initiate dataset
            ds = Dataset()
            # Set required DICOM attributes

            # Update and insert additional DICOM attributes as available
            ds = update_and_insert_additional_DICOM_attributes_in_ds(ds, sequence_item)
            # Add dataset to sequence
            self.sequence.append(ds)


def generate_sequence(sequence_name, sequence_data):
    """Helper function to generate appropriate sequences
    Parameters
    ----------
    sequence_name : Name of sequence to generate
    sequence_data : List of items with data to generate each sequence item,
                    in the format of a list with a dictionary for each item,
                    which in turn can contain a sequence, e.g. list of dictionaries
    """
    if sequence_name == "ConceptNameCodeSequence":
        return ConceptNameCodeSequence(sequence_data).get_sequence()
    elif sequence_name == "ConceptCodeSequence":
        return ConceptCodeSequence(sequence_data).get_sequence()
    elif sequence_name == "ContentSequence":
        return ContentSequence(sequence_data).get_sequence()
    elif sequence_name == "ContentTemplateSequence":
        return ContentTemplateSequence(sequence_data).get_sequence()
    elif sequence_name == "CurrentRequestedProcedureEvidenceSequence":
        return CurrentRequestedProcedureEvidenceSequence(sequence_data).get_sequence()
    elif sequence_name == "PerformedProcedureCodeSequence":
        return PerformedProcedureCodeSequence(sequence_data).get_sequence()
    elif sequence_name == "MeasuredValueSequence":
        return MeasuredValueSequence(sequence_data).get_sequence()
    elif sequence_name == "MeasurementUnitsCodeSequence":
        return MeasurementUnitsCodeSequence(sequence_data).get_sequence()
    elif sequence_name == "ReferencedSeriesSequence":
        return ReferencedSeriesSequence(sequence_data).get_sequence()
    elif sequence_name == "ReferencedSOPSequence":
        return ReferencedSOPSequence(sequence_data).get_sequence()
    elif sequence_name == "ReferencedImageSequence":
        return ReferencedImageSequence(sequence_data).get_sequence()
    elif sequence_name == "DisplayedAreaSelectionSequence":
        return DisplayedAreaSelectionSequence(sequence_data).get_sequence()
    elif sequence_name == "GraphicAnnotationSequence":
        return GraphicAnnotationSequence(sequence_data).get_sequence()
    elif sequence_name == "GraphicObjectSequence":
        return GraphicObjectSequence(sequence_data).get_sequence()
    elif sequence_name == "TextObjectSequence":
        return TextObjectSequence(sequence_data).get_sequence()
    elif sequence_name == "TextStyleSequence":
        return TextStyleSequence(sequence_data).get_sequence()
    elif sequence_name == "LineStyleSequence":
        return LineStyleSequence(sequence_data).get_sequence()
    elif sequence_name == "FillStyleSequence":
        return FillStyleSequence(sequence_data).get_sequence()
    elif sequence_name == "GraphicLayerSequence":
        return GraphicLayerSequence(sequence_data).get_sequence()
    elif sequence_name == "SoftcopyVOILUTSequence":
        return SoftcopyVOILUTSequence(sequence_data).get_sequence()
    else:
        return GeneralSequence(sequence_data).get_sequence()
