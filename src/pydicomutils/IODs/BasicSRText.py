from datetime import datetime

from pydicom import Dataset, uid, read_file

from .IOD import IOD, IODTypes, SOP_CLASS_UID_MODALITY_DICT
from .modules.specific_sr_modules import SRDocumentSeriesModule, SRDocumentGeneralModule
from .modules.specific_sr_modules import SRDocumentContentModule
from .sequences.Sequences import generate_sequence, generate_CRPES_sequence

class BasicSRText(IOD):
    """Implementation of the Basic SR Text IOD
    """
    def __init__(self):
        super().__init__(IODTypes.BasicTextSR)

    def create_empty_iod(self):
        """Creates and empty IOD with the required DICOM tags but no values
        Parameters
        ----------
        """
        super().create_empty_iod()

        self.copy_required_dicom_attributes(Dataset(), include_optional=True)

    def copy_required_dicom_attributes(self, dataset_to_copy_from,
                                       include_iod_specific=True,
                                       include_optional=False):
        """Copies required DICOM attributes from provided dataset
        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        include_iod_specific : Include IOD specific DICOM attributes in copy (True)
        include_optional : Include optional DICOM attributes in copy (False)
        """
        super().copy_required_dicom_attributes(dataset_to_copy_from,
                                               include_optional)

        if include_iod_specific:
            sr_specific_modules = [SRDocumentSeriesModule(),
                                   SRDocumentGeneralModule(),
                                   SRDocumentContentModule()]
            for module in sr_specific_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                      self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                          self.dataset)
    
    def initiate(self, referenced_dcm_files=None):
        """Initiate the IOD by setting some dummy values for
        required attributes
        
        Keyword Arguments:
            referenced_dcm_files {[dcm_file1, dcm_file2, ...]} -- List of file paths (default: {None})
        """
        super().initiate()
        if referenced_dcm_files:
            # some attributes to inherit from referenced dcm files
            ds = read_file(referenced_dcm_files[0])
            self.dataset.PatientID = ds.PatientID
            self.dataset.PatientName = ds.PatientName
            self.dataset.PatientSex = ds.PatientSex
            self.dataset.PatientBirthDate = ds.PatientBirthDate
            self.dataset.StudyInstanceUID = ds.StudyInstanceUID
            self.dataset.StudyID = ds.StudyID
            self.dataset.AccessionNumber = ds.AccessionNumber
            if "StudyDescription" in ds:
                self.dataset.StudyDescription = ds.StudyDescription
            self.dataset.StudyDate = ds.StudyDate
            self.dataset.StudyTime = ds.StudyTime
        # sr document series module
        self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
        self.dataset.SeriesInstanceUID = uid.generate_uid()
        # sr document general module
        self.dataset.InstanceNumber = str(1)
        self.dataset.CompletionFlag = "COMPLETE"
        self.dataset.VerificationFlag = "UNVERIFIED"
        self.dataset.ContentDate = datetime.now().strftime("%Y%m%d")
        self.dataset.ContentTime = datetime.now().strftime("%H%M%S")
        self.dataset.PerformedProcedureCodeSequence = generate_sequence("PerformedProcedureCodeSequence", [])
        if referenced_dcm_files:
            self.dataset.CurrentRequestedProcedureEvidenceSequence = generate_CRPES_sequence(referenced_dcm_files)
        self.dataset.PreliminaryFlag = "FINAL"

        # sr document content module
        self.dataset.ValueType = "CONTAINER"
        self.dataset.ConceptNameCodeSequence = generate_sequence("ConceptNameCodeSequence", 
                                                                 [{
                                                                     "CodeValue": "128005", 
                                                                     "CodingSchemeDesignator": "DCM", 
                                                                     "CodeMeaning": "Final Report"
                                                                 }])
        self.dataset.ContinuityOfContent = "SEPARATE"

    def add_text_node(self, text_value, concept_name_code):
        """Inserts a text node into the ContentSequence of the basic SR report
        
        Arguments:
            text_value {str} -- Text value
            concept_name_code {[str, str, str]} -- CodeValue, CodingschemeDesignator and CodeMeaning
        """
        ds = Dataset()
        ds.RelationshipType = "CONTAINS"
        ds.ValueType = "TEXT"
        ds.ConceptNameCodeSequence = generate_sequence("ConceptNameCodeSequence",
                                                       [{
                                                           "CodeValue": concept_name_code[0], 
                                                           "CodingSchemeDesignator": concept_name_code[1], 
                                                           "CodeMeaning": concept_name_code[2]
                                                       }])
        ds.TextValue = text_value
        self.dataset.ContentSequence.append(ds)