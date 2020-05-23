import random
from datetime import datetime
from enum import Enum

from pydicom import Dataset, FileDataset, DataElement, Sequence, write_file, read_file, uid
from pydicom.datadict import tag_for_keyword, dictionary_VR

from .modules.general_modules import PatientModule, GeneralStudyModule
from .modules.general_modules import GeneralSeriesModule, GeneralEquipmentModule, EnhancedGeneralEquipmentModule
from .modules.general_modules import GeneralImageModule, ImagePixelModule
from .modules.general_modules import SOPCommonModule
from .sequences.Sequences import generate_sequence

class IODTypes(Enum):
    """Definition of different IODs and their corresponding SOP Class UIDs
    """
    CRImage =     "1.2.840.10008.5.1.4.1.1.1"
    CTImage =     "1.2.840.10008.5.1.4.1.1.2"
    SCImage =     "1.2.840.10008.5.1.4.1.1.7"
    GSPS =        "1.2.840.10008.5.1.4.1.1.11.1"
    CSPS =        "1.2.840.10008.5.1.4.1.1.11.2"
    BasicTextSR = "1.2.840.10008.5.1.4.1.1.88.11"
    EnhancedSR =  "1.2.840.10008.5.1.4.1.1.88.22"
    KOS =         "1.2.840.10008.5.1.4.1.1.88.59"
    WSMImage =    "1.2.840.10008.5.1.4.1.1.77.1.6"

"""Dictionary to go from SOPClassUID to Modality code
"""
SOP_CLASS_UID_MODALITY_DICT = {
    IODTypes.CRImage: "CR",
    IODTypes.CTImage: "CT",
    IODTypes.SCImage: "SC",
    IODTypes.GSPS: "PR",
    IODTypes.CSPS: "PR",
    IODTypes.BasicTextSR: "SR",
    IODTypes.EnhancedSR: "SR",
    IODTypes.KOS: "KO",
    IODTypes.WSMImage: "SM"
}

class IOD:
    """Basic IOD class
    """
    iod_type = None
    dataset = None

    def __init__(self, iod_type):
        """
        Parameters
        ----------
        iod_type : Type of IOD, i.e. DICOM object of class IODTypes
        """
        self.iod_type = iod_type
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = iod_type.value
        file_meta.MediaStorageSOPInstanceUID = uid.generate_uid()
        file_meta.ImplementationClassUID = "1.2.752.24.16.4.1"
        self.dataset = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
        self.dataset.is_little_endian = True
        self.dataset.is_implicit_VR = False
        self.dataset.file_meta.TransferSyntaxUID = uid.ExplicitVRLittleEndian

    def create_empty_iod(self):
        """Creates and empty IOD with the required DICOM tags but no values
        Parameters
        ----------
        """
        self.copy_required_dicom_attributes(Dataset(), include_optional=True)

    def set_dicom_attribute(self, keyword, value):
        """Sets specified DICOM attribute according to the keyword value pair
        Parameters
        ----------
        keyword : Name of DICOM tag to set value for
        value : Value to set
        """
        if tag_for_keyword(keyword):
            if keyword in self.dataset:
                if dictionary_VR(tag_for_keyword(keyword)) == "SQ" and isinstance(value, list):
                    value = generate_sequence(keyword, value)
                self.dataset[tag_for_keyword(keyword)].value = value
            else:
                if dictionary_VR(tag_for_keyword(keyword)) == "SQ" and isinstance(value, list):
                    value = generate_sequence(keyword, value)
                de = DataElement(tag_for_keyword(keyword), 
                                 dictionary_VR(tag_for_keyword(keyword)), 
                                 value)
                self.dataset[tag_for_keyword(keyword)] = de
        else:
            print("Keyword", keyword,"is an unknown DICOM attribute")

    def copy_required_dicom_attributes(self, dataset_to_copy_from, 
                                       include_optional=True):
        """Copies required DICOM attributes from provided dataset
        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        include_optional : Include optional DICOM attributes in copy
        """
        general_modules = [PatientModule(),
                           GeneralStudyModule(),
                           GeneralEquipmentModule(),
                           SOPCommonModule()]
        for module in general_modules:
            module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                  self.dataset)
            if include_optional:
                module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                      self.dataset)

        if self.iod_type in [IODTypes.WSMImage]:
            general_modules = [EnhancedGeneralEquipmentModule()]
            for module in general_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                      self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                          self.dataset)

        if self.iod_type in [IODTypes.CRImage, IODTypes.CTImage, IODTypes.SCImage, IODTypes.WSMImage]:
            general_image_modules = [GeneralImageModule(),
                                     GeneralSeriesModule(),
                                     ImagePixelModule()]
            for module in general_image_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                      self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                          self.dataset)

        if self.iod_type in [IODTypes.GSPS, IODTypes.CSPS]:
            general_series_modules = [GeneralSeriesModule()]
            for module in general_series_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                    self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                          self.dataset)

    def initiate(self):
        """Initiate the IOD by setting some dummy values for
        required attributes
        """
        # patient module
        self.dataset.PatientID = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        # general study module
        self.dataset.StudyInstanceUID = uid.generate_uid()
        self.dataset.StudyDate = datetime.now().strftime("%Y%m%d")
        self.dataset.StudyTime = datetime.now().strftime("%H%M%S")
        self.dataset.StudyID = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        self.dataset.AccessionNumber = self.dataset.StudyID
        # sop common module
        self.dataset.SOPClassUID = self.iod_type.value
        self.dataset.SOPInstanceUID = uid.generate_uid()

        if self.iod_type in [IODTypes.CRImage, IODTypes.CTImage, IODTypes.SCImage, IODTypes.WSMImage]:
            # general series module
            self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
            self.dataset.SeriesInstanceUID = uid.generate_uid()
            self.dataset.SeriesNumber = str(100)
            # general image module
            self.dataset.InstanceNumber = str(1)
            self.dataset.ContentDate = datetime.now().strftime("%Y%m%d")
            self.dataset.ContentTime = datetime.now().strftime("%H%M%S")

        if self.iod_type in [IODTypes.GSPS, IODTypes.CSPS]:
            # general series module
            self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
            self.dataset.SeriesInstanceUID = uid.generate_uid()
            self.dataset.SeriesNumber = str(100)
            
        
    def write_to_file(self, output_file, write_like_original=False):
        """Writes the current IOD to file
        Parameters
        ----------
        output_file : Complete path of file to write to
        """
        write_file(output_file, self.dataset, write_like_original=write_like_original)
