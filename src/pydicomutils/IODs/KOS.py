from datetime import datetime

from pydicom import Dataset, read_file, uid

from .IOD import IOD, IODTypes, SOP_CLASS_UID_MODALITY_DICT
from .modules.specific_sr_modules import (
    KeyObjectDocumentSeriesModule,
    KeyObjectDocumentModule,
)
from .modules.specific_sr_modules import SRDocumentContentModule
from .sequences.Sequences import generate_sequence, generate_CRPES_sequence


class KOS(IOD):
    """Implementation of the Key Object Selection Document IOD
    """

    def __init__(self):
        super().__init__(IODTypes.KOS)

    def create_empty_iod(self):
        """Creates and empty IOD with the required DICOM tags but no values

        Parameters
        ----------
        """
        super().create_empty_iod()

        self.copy_required_dicom_attributes(Dataset(), include_optional=True)

    def copy_required_dicom_attributes(
        self, dataset_to_copy_from, include_iod_specific=True, include_optional=False
    ):
        """Copies required DICOM attributes from provided dataset

        Parameters
        ----------
        dataset_to_copy_from : Dataset to copy DICOM attributes from
        include_iod_specific : Include IOD specific DICOM attributes in copy (True)
        include_optional : Include optional DICOM attributes in copy (False)
        """
        super().copy_required_dicom_attributes(dataset_to_copy_from, include_optional)

        if include_iod_specific:
            sr_specific_modules = [
                KeyObjectDocumentSeriesModule(),
                KeyObjectDocumentModule(),
                SRDocumentContentModule(),
            ]
            for module in sr_specific_modules:
                module.copy_required_dicom_attributes(
                    dataset_to_copy_from, self.dataset
                )
                if include_optional:
                    module.copy_optional_dicom_attributes(
                        dataset_to_copy_from, self.dataset
                    )

    def initiate(self, referenced_dcm_files=None):
        """Initiate the IOD by setting some dummy values for required attributes
        
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
        # key object document series module
        self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
        self.dataset.SeriesInstanceUID = uid.generate_uid()
        self.dataset.SeriesNumber = str(600)
        # key object document module
        self.dataset.InstanceNumber = str(1)
        self.dataset.ContentDate = datetime.now().strftime("%Y%m%d")
        self.dataset.ContentTime = datetime.now().strftime("%H%M%S")
        if referenced_dcm_files:
            self.dataset.CurrentRequestedProcedureEvidenceSequence = generate_CRPES_sequence(
                referenced_dcm_files
            )
        # sr document content module
        self.dataset.ValueType = "CONTAINER"
        self.dataset.ConceptNameCodeSequence = generate_sequence(
            "ConceptNameCodeSequence",
            [
                {
                    "CodeValue": "113000",
                    "CodingSchemeDesignator": "DCM",
                    "CodeMeaning": "Of Interest",
                }
            ],
        )
        self.dataset.ContinuityOfContent = "SEPARATE"
        self.dataset.ContentTemplateSequence = generate_sequence(
            "ContentTemplateSequence",
            [{"MappingResource": "DCMR", "TemplateIdentifier": "2010"}],
        )

    def add_key_documents(self, referenced_dcm_files, referenced_frames=None):
        """Add key document
        
        Arguments:
            referenced_dcm_files {[type]} -- [description]
            referenced_frames {[type]} -- [description]
        """
        if referenced_frames is None:
            for referenced_dcm_file in referenced_dcm_files:
                ds = Dataset()
                ds_ref = read_file(referenced_dcm_file)
                ds.ReferencedSOPSequence = generate_sequence(
                    "ReferencedSOPSequence",
                    [
                        {
                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                        }
                    ],
                )
                ds.RelationshipType = ("CONTAINS",)
                ds.ValueType = "IMAGE"
                self.dataset.ContentSequence.append(ds)
        else:
            if len(referenced_dcm_files) != len(referenced_frames):
                print(
                    "Number of referenced DCM files is expected to correspond to the number of referenced frames"
                )
                exit
            else:
                for referenced_dcm_file, referenced_frame_numbers in zip(
                    referenced_dcm_files, referenced_frames
                ):
                    ds = Dataset()
                    ds_ref = read_file(referenced_dcm_file)
                    ds.ReferencedSOPSequence = generate_sequence(
                        "ReferencedSOPSequence",
                        [
                            {
                                "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                "ReferencedFrameNumber": referenced_frame_numbers,
                            }
                        ],
                    )
                    ds.RelationshipType = ("CONTAINS",)
                    ds.ValueType = "IMAGE"
                    self.dataset.ContentSequence.append(ds)

