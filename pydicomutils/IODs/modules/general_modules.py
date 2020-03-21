from pydicom import Dataset, DataElement
from pydicom.datadict import tag_for_keyword, dictionary_VR

class Module:
    """Basic Module class
    """
    required_dicom_attributes = None
    optional_dicom_attributes = None

    def __init__(self):
        self.required_dicom_attributes = list()
        self.optional_dicom_attributes = list()

    def copy_required_dicom_attributes(self, dataset_to_copy_from, dataset_to_copy_to):
        """Copies required DICOM attributes for this module from one dataset to another
        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        dataset_to_copy_to : Dataset to copy DICOM attributes to
        """
        for dicom_attribute in self.required_dicom_attributes:
            tag = tag_for_keyword(dicom_attribute)
            if dicom_attribute in dataset_to_copy_from:
                dataset_to_copy_to[tag] = dataset_to_copy_from[tag]
            elif dicom_attribute in dataset_to_copy_to:
                pass
            else:
                de = DataElement(tag, dictionary_VR(tag), "")
                dataset_to_copy_to[tag] = de

    def copy_optional_dicom_attributes(self, dataset_to_copy_from, dataset_to_copy_to):
        """Copies optional DICOM attributes for this module from one dataset to another
        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        dataset_to_copy_to : Dataset to copy DICOM attributes to
        """
        for dicom_attribute in self.optional_dicom_attributes:
            tag = tag_for_keyword(dicom_attribute)
            if dicom_attribute in dataset_to_copy_from:
                dataset_to_copy_to[tag] = dataset_to_copy_from[tag]
            elif dicom_attribute in dataset_to_copy_to:
                pass
            else:
                de = DataElement(tag, dictionary_VR(tag), "")
                dataset_to_copy_to[tag] = de

    def copy_additional_dicom_attributes(self, dataset_to_copy_from, dataset_to_copy_to,
                                         additional_dicom_attributes):
        """Copies additional DICOM attributes for this module from one dataset to another
        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        dataset_to_copy_to : Dataset to copy DICOM attributes to
        additional_dicom_attributes : List of additional DICOM attributes to copy
        """
        for dicom_attribute in additional_dicom_attributes:
            tag = tag_for_keyword(dicom_attribute)
            if dicom_attribute in dataset_to_copy_from:
                dataset_to_copy_to[tag] = dataset_to_copy_from[tag]
            else:
                de = DataElement(tag, dictionary_VR(tag), "")
                dataset_to_copy_to[tag] = de

class PatientModule(Module):
    """Patient Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PatientName",
                                          "PatientID",
                                          "PatientBirthDate",
                                          "PatientSex"]

class GeneralStudyModule(Module):
    """General Study Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["StudyInstanceUID",
                                          "StudyDate",
                                          "StudyTime",
                                          "ReferringPhysicianName",
                                          "StudyID",
                                          "AccessionNumber"]
        self.optional_dicom_attributes = ["StudyDescription"]

class GeneralEquipmentModule(Module):
    """General Equipment Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Manufacturer"]

class EnhancedGeneralEquipmentModule(Module):
    """Enhanced General Equipment Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Manufacturer",
                                          "ManufacturerModelName",
                                          "DeviceSerialNumber",
                                          "SoftwareVersions"]

class SOPCommonModule(Module):
    """SOP Common Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["SOPClassUID",
                                          "SOPInstanceUID"]
        self.optional_dicom_attributes = ["InstanceNumber"]
        
class GeneralSeriesModule(Module):
    """General Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Modality",
                                          "SeriesInstanceUID",
                                          "SeriesNumber",
                                          "Laterality"]
        self.optional_dicom_attributes = ["SeriesDate",
                                          "SeriesTime",
                                          "SeriesDescription",
                                          "BodyPartExamined"]

class GeneralImageModule(Module):
    """General Image Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["InstanceNumber",
                                          "PatientOrientation",
                                          "ContentDate",
                                          "ContentTime"]
        self.optional_dicom_attributes = ["ImageType",
                                          "AcquisitionNumber",
                                          "AcquisitionDate",
                                          "AcquisitionTime",
                                          "ImagesInAcquisition",
                                          "ImageComments"]

class FrameOfReferenceModule(Module):
    """Frame Of Reference Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["FrameOfReferenceUID",
                                          "PositionReferenceIndicator"]
        
class ImagePixelModule(Module):
    """Image Pixel Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["SamplesPerPixel",
                                          "PhotometricInterpretation",
                                          "Rows",
                                          "Columns",
                                          "BitsAllocated",
                                          "BitsStored",
                                          "HighBit",
                                          "PixelRepresentation",
                                          "PixelData"]

class ImagePlaneModule(Module):
    """Image Plane Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PixelSpacing",
                                          "ImageOrientationPatient",
                                          "ImagePositionPatient",
                                          "SliceThickness"]

class AcquisitionContextModule(Module):
    """Acquisition Context Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["AcquisitionContextSequence"]

class MultiFrameFunctionalGroupsModule(Module):
    """Multi-frame Functional Groups Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["SharedFunctionalGroupsSequence",
                                          "InstanceNumber",
                                          "ContentDate",
                                          "ContentTime",
                                          "NumberOfFrames"]

class MultiFrameDimensionModule(Module):
    """Multi-frame Dimension Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["DimensionOrganizationSequence",
                                          "DimensionIndexSequence"]

class SpecimenModule(Module):
    """Specimen Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ContainerIdentifier",
                                          "IssuerOfTheContainerIdentifierSequence",
                                          "ContainerTypeCodeSequence",
                                          "SpecimenDescriptionSequence"]

class CommonInstanceReferenceModule(Module):
    """Common Instance Reference Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = []