import os
import random
from datetime import datetime

from pydicom import Dataset, dcmread
from pydicom.uid import generate_uid

from .IOD import IOD, IODTypes, SOP_CLASS_UID_MODALITY_DICT
from .modules.specific_sr_modules import SRDocumentSeriesModule, SRDocumentGeneralModule
from .modules.specific_sr_modules import SRDocumentContentModule
from .sequences.Sequences import (
    generate_sequence,
    generate_CRPES_sequence,
    update_and_insert_additional_DICOM_attributes_in_ds,
)
from .sequences.Sequences import generate_reference_sop_sequence_json


class EnhancedSRTID1500(IOD):
    """Implementation of the Enhanced SR IOD using Template ID 1500"""

    def __init__(self):
        super().__init__(IODTypes.EnhancedSR)

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
                SRDocumentSeriesModule(),
                SRDocumentGeneralModule(),
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

    def initiate(self, referenced_dcms=None):
        """Initiate the IOD by setting some dummy values for required attributes

        Keyword Arguments:
            referenced_dcms {[dcm_file1, dcm_file2, ...]} -- List of file paths (default: {None})
        """
        super().initiate()
        if referenced_dcms:
            # some attributes to inherit from referenced dcm files
            ds = None
            if isinstance(referenced_dcms[0], Dataset):
                ds = referenced_dcms[0]
            else:
                ds = dcmread(referenced_dcms[0])
            self.dataset.PatientID = ds.PatientID
            self.dataset.PatientName = ds.PatientName
            self.dataset.PatientSex = ds.PatientSex
            self.dataset.PatientBirthDate = (
                ds.PatientBirthDate if "PatientBirthDate" in ds else ""
            )
            self.dataset.StudyInstanceUID = ds.StudyInstanceUID
            self.dataset.StudyID = ds.StudyID
            self.dataset.AccessionNumber = ds.AccessionNumber
            if "StudyDescription" in ds:
                self.dataset.StudyDescription = ds.StudyDescription
            self.dataset.StudyDate = ds.StudyDate
            self.dataset.StudyTime = ds.StudyTime
        # sr document series module
        self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
        self.dataset.SeriesInstanceUID = generate_uid()
        # sr document general module
        self.dataset.InstanceNumber = str(1)
        self.dataset.CompletionFlag = "COMPLETE"
        self.dataset.VerificationFlag = "UNVERIFIED"
        self.dataset.ContentDate = datetime.now().strftime("%Y%m%d")
        self.dataset.ContentTime = datetime.now().strftime("%H%M%S")
        if referenced_dcms:
            self.dataset.CurrentRequestedProcedureEvidenceSequence = (
                generate_CRPES_sequence(referenced_dcms)
            )
        self.dataset.PreliminaryFlag = "FINAL"
        # sr document content module
        self.dataset.ValueType = "CONTAINER"
        self.dataset.ConceptNameCodeSequence = generate_sequence(
            "ConceptNameCodeSequence",
            [
                {
                    "CodeValue": "126000",
                    "CodingSchemeDesignator": "DCM",
                    "CodeMeaning": "Imaging Measurement Report",
                }
            ],
        )
        self.dataset.ContentTemplateSequence = generate_sequence(
            "ContentTemplateSequence",
            [
                {
                    "MappingResource": "DCMR",
                    "MappingResourceUID": "1.2.840.10008.8.1.1",
                    "TemplateIdentifier": "1500",
                }
            ],
        )
        self.dataset.ContinuityOfContent = "SEPARATE"
        self.dataset.ContentSequence = generate_sequence(
            "ContentSequence",
            [
                {
                    "RelationshipType": "HAS CONCEPT MOD",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121049",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Language of Content Item and Descendants",
                        }
                    ],
                    "ConceptCodeSequence": [
                        {
                            "CodeValue": "eng",
                            "CodingSchemeDesignator": "RFC5646",
                            "CodeMeaning": "English",
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "HAS CONCEPT MOD",
                            "ValueType": "CODE",
                            "ConceptNameCodeSequence": [
                                {
                                    "CodeValue": "121046",
                                    "CodingSchemeDesignator": "DCM",
                                    "CodeMeaning": "Country of Language",
                                }
                            ],
                            "ConceptCodeSequence": [
                                {
                                    "CodeValue": "US",
                                    "CodingSchemeDesignator": "ISO3166_1",
                                    "CodeMeaning": "United States",
                                }
                            ],
                        }
                    ],
                },
                {
                    "RelationshipType": "HAS CONCEPT MOD",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121058",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Procedure Reported",
                        }
                    ],
                    "ConceptCodeSequence": [
                        {
                            "CodeValue": "363679005",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Imaging Procedure",
                        }
                    ],
                },
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CONTAINER",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "111028",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Image Library",
                        }
                    ],
                    "ContinuityOfContent": "SEPARATE",
                    "ContentSequence": [
                        {
                            "RelationshipType": "CONTAINS",
                            "ValueType": "CONTAINER",
                            "ConceptNameCodeSequence": [
                                {
                                    "CodeValue": "126200",
                                    "CodingSchemeDesignator": "DCM",
                                    "CodeMeaning": "Image Library Group",
                                }
                            ],
                            "ContinuityOfContent": "SEPARATE",
                            "ContentSequence": [
                                generate_reference_sop_sequence_json(dcm_file)
                                for dcm_file in referenced_dcms
                            ],
                        }
                    ],
                },
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CONTAINER",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "126010",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Imaging Measurements",
                        }
                    ],
                    "ContinuityOfContent": "SEPARATE",
                    "ContentSequence": [],
                },
            ],
        )

    def initiate_measurement_group(self):
        """Initiate a measurement group

        Returns:
            [type] -- [description]
        """
        ds = Dataset()
        ds.RelationshipType = "CONTAINS"
        ds.ValueType = "CONTAINER"
        ds.ConceptNameCodeSequence = generate_sequence(
            "ConceptNameCodeSequence",
            [
                {
                    "CodeValue": "125007",
                    "CodingSchemeDesignator": "DCM",
                    "CodeMeaning": "Measurement Group",
                }
            ],
        )
        ds.ContinuityOfContent = "SEPARATE"
        # ds.ContentTemplateSequence = generate_sequence("ContentTemplateSequence", [{
        #     "MappingResource": "DCMR",
        #     "MappingResourceUID": "1.2.840.10008.8.1.1",
        #     "TemplateIdentifier": "1411"}])
        return ds

    def initiate_content_sequence(
        self, tracking_id, tracking_uid, finding, finding_site
    ):
        """Initiate a content sequence

        Arguments:
            tracking_id {[type]} -- [description]
            tracking_uid {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]
        """
        return generate_sequence(
            "ContentSequence",
            [
                {
                    "RelationshipType": "HAS OBS CONTEXT",
                    "ValueType": "TEXT",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "112039",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Tracking Identifier",
                        }
                    ],
                    "TextValue": tracking_id,
                },
                {
                    "RelationshipType": "HAS OBS CONTEXT",
                    "ValueType": "UIDREF",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "112040",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Tracking Unique Identifier",
                        }
                    ],
                    "UID": tracking_uid,
                },
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121071",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Finding",
                        }
                    ],
                    "ConceptCodeSequence": [
                        {
                            "CodeValue": finding[0],
                            "CodingSchemeDesignator": finding[1],
                            "CodeMeaning": finding[2],
                        }
                    ],
                },
                {
                    "RelationshipType": "HAS CONCEPT MOD",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "363698007",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Finding Site",
                        }
                    ],
                    "ConceptCodeSequence": [
                        {
                            "CodeValue": finding_site[0],
                            "CodingSchemeDesignator": finding_site[1],
                            "CodeMeaning": finding_site[2],
                        }
                    ],
                },
            ],
        )

    def add_qualitative_evaluations(self, ds, qualitative_evaluations):
        """Add a qualitative evaluation

        Arguments:
            ds {[type]} -- [description]
            qualitative_evaluations {[type]} -- [description]
        """
        for item in qualitative_evaluations:
            if item is None:
                continue
            if "text_value" in item:
                ds.ContentSequence.append(
                    update_and_insert_additional_DICOM_attributes_in_ds(
                        Dataset(),
                        {
                            "RelationshipType": "CONTAINS",
                            "ValueType": "TEXT",
                            "ConceptNameCodeSequence": [
                                {
                                    "CodeValue": "C00034375",
                                    "CodingSchemeDesignator": "UMLS",
                                    "CodeMeaning": "Qualitative Evaluations",
                                }
                            ],
                            "TextValue": item["text_value"],
                        },
                    )
                )
            else:
                ds.ContentSequence.append(
                    update_and_insert_additional_DICOM_attributes_in_ds(
                        Dataset(),
                        {
                            "RelationshipType": "CONTAINS",
                            "ValueType": "CODE",
                            "ConceptNameCodeSequence": [
                                {
                                    "CodeValue": "C00034375",
                                    "CodingSchemeDesignator": "UMLS",
                                    "CodeMeaning": "Qualitative Evaluations",
                                }
                            ],
                            "ConceptCodeSequence": [
                                {
                                    "CodeValue": item["code_value"][0],
                                    "CodingSchemeDesignator": item["code_value"][1],
                                    "CodeMeaning": item["code_value"][2],
                                }
                            ],
                        },
                    )
                )
        return ds

    def add_coded_values(self, ds, coded_values):
        """Add coded values

        Arguments:
            ds {[type]} -- [description]
            qualitative_evaluations {[type]} -- [description]
        """
        for item in coded_values:
            if item is None:
                continue
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "HAS CONCEPT MOD",
                        "ValueType": "CODE",
                        "ConceptNameCodeSequence": [
                            {
                                "CodeValue": item["ConceptNameCode"][0],
                                "CodingSchemeDesignator": item["ConceptNameCode"][1],
                                "CodeMeaning": item["ConceptNameCode"][2],
                            }
                        ],
                        "ConceptCodeSequence": [
                            {
                                "CodeValue": item["ConceptCode"][0],
                                "CodingSchemeDesignator": item["ConceptCode"][1],
                                "CodeMeaning": item["ConceptCode"][2],
                            }
                        ],
                    },
                )
            )
        return ds

    def add_text_values(self, ds, text_values):
        """Add text values

        Arguments:
            ds {[type]} -- [description]
            qualitative_evaluations {[type]} -- [description]
        """
        for item in text_values:
            if item is None:
                continue
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "HAS CONCEPT MOD",
                        "ValueType": "TEXT",
                        "ConceptNameCodeSequence": [
                            {
                                "CodeValue": item["ConceptNameCode"][0],
                                "CodingSchemeDesignator": item["ConceptNameCode"][1],
                                "CodeMeaning": item["ConceptNameCode"][2],
                            }
                        ],
                        "TextValue": item["TextValue"],
                    },
                )
            )
        return ds

    def add_landmark(
        self,
        dcm_file,
        graphic_data,
        finding,
        finding_site,
        tracking_id=None,
        tracking_uid=None,
        qualitative_evaluations=None,
        coded_values=None,
        text_values=None,
    ):
        """Add landmark value

        Arguments:
            dcm_file {[type]} -- [description]
            graphic_data {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]

        Keyword Arguments:
            tracking_id {[type]} -- [description] (default: {None})
            tracking_uid {[type]} -- [description] (default: {None})
        """
        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        ds_ref = dcmread(dcm_file)
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        if coded_values is not None:
            ds = self.add_coded_values(ds, coded_values)
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "758637006",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Anatomical locations",
                        }
                    ],
                    "ConceptCodeSequence": [
                        {
                            "CodeValue": "26216008",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Center",
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": [
                                        {
                                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                        }
                                    ],
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data,
                            "GraphicType": "POINT",
                        }
                    ],
                },
            )
        )
        if text_values is not None:
            ds = self.add_text_values(ds, text_values)
        if qualitative_evaluations is not None:
            ds = self.add_qualitative_evaluations(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)

    def add_unmeasurable_measurement(
        self,
        dcm_file,
        graphic_data,
        finding,
        finding_site,
        reason,
        tracking_id=None,
        tracking_uid=None,
    ):
        """Add an unmeasurable measurement

        Arguments:
            dcm_file {[type]} -- [description]
            graphic_data {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]

        Keyword Arguments:
            tracking_id {[type]} -- [description] (default: {None})
            tracking_uid {[type]} -- [description] (default: {None})
        """
        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        ds_ref = dcmread(dcm_file)
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "TEXT",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "C00034375",
                            "CodingSchemeDesignator": "UMLS",
                            "CodeMeaning": "Qualitative Evaluations",
                        }
                    ],
                    "TextValue": reason,
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": [
                                        {
                                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                        }
                                    ],
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data,
                            "GraphicType": "CIRCLE",
                        }
                    ],
                },
            )
        )
        self.dataset.ContentSequence[3].ContentSequence.append(ds)

    def add_linear_measurement_single_axis(
        self,
        dcm_ref,
        linear_measurement,
        graphic_data,
        measurement_type,
        finding,
        finding_site,
        tracking_id=None,
        tracking_uid=None,
        qualitative_evaluations=None,
        coded_values=None,
        text_values=None,
    ):
        """Add linear measurement

        Arguments:
            dcm_file {[type]} -- [description]
            linear_measurement {[type]} -- [description]
            graphic_data {[type]} -- [description]
            measurement_type {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]
        """
        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        referenced_sop_sequence = None
        if isinstance(dcm_ref, str):
            ds_ref = dcmread(dcm_ref)
            referenced_sop_sequence = [
                {
                    "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                    "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                }
            ]
        else:
            referenced_sop_sequence = [
                {
                    "ReferencedSOPClassUID": dcm_ref.ReferencedSOPClassUID,
                    "ReferencedSOPInstanceUID": dcm_ref.ReferencedSOPInstanceUID,
                }
            ]
            if "ReferencedFrameNumber" in dcm_ref:
                referenced_sop_sequence[0][
                    "ReferencedFrameNumber"
                ] = dcm_ref.ReferencedFrameNumber
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        if coded_values is not None:
            ds = self.add_coded_values(ds, coded_values)
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": measurement_type[0],
                            "CodingSchemeDesignator": measurement_type[1],
                            "CodeMeaning": measurement_type[2],
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "millimeter",
                                }
                            ],
                            "NumericValue": linear_measurement,
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": referenced_sop_sequence,
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data,
                            "GraphicType": "POLYLINE",
                        }
                    ],
                },
            )
        )
        if text_values is not None:
            ds = self.add_text_values(ds, text_values)
        if qualitative_evaluations is not None:
            ds = self.add_qualitative_evaluations(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)

    def add_linear_measurement_double_axis(
        self,
        dcm_file,
        linear_measurement_axis1,
        graphic_data_axis1,
        measurement_type_axis1,
        linear_measurement_axis2,
        graphic_data_axis2,
        measurement_type_axis2,
        finding,
        finding_site,
        tracking_id=None,
        tracking_uid=None,
        qualitative_evaluations=None,
        coded_values=None,
        text_values=None,
    ):
        """Add linear measurement with two axis

        Arguments:
            dcm_file {[type]} -- [description]
            linear_measurement_axis1 {[type]} -- [description]
            graphic_data_axis1 {[type]} -- [description]
            measurement_type_axis1 {[type]} -- [description]
            linear_measurement_axis2 {[type]} -- [description]
            graphic_data_axis2 {[type]} -- [description]
            measurement_type_axis2 {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]
            tracking_id {[type]} -- [description]
            tracking_uid {[type]} -- [description]
        """
        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        ds_ref = dcmread(dcm_file)
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        if coded_values is not None:
            ds = self.add_coded_values(ds, coded_values)
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": measurement_type_axis1[0],
                            "CodingSchemeDesignator": measurement_type_axis1[1],
                            "CodeMeaning": measurement_type_axis1[2],
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "millimeter",
                                }
                            ],
                            "NumericValue": linear_measurement_axis1,
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": [
                                        {
                                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                        }
                                    ],
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data_axis1,
                            "GraphicType": "POLYLINE",
                        }
                    ],
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": measurement_type_axis2[0],
                            "CodingSchemeDesignator": measurement_type_axis2[1],
                            "CodeMeaning": measurement_type_axis2[2],
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "millimeter",
                                }
                            ],
                            "NumericValue": linear_measurement_axis2,
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": [
                                        {
                                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                        }
                                    ],
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data_axis2,
                            "GraphicType": "POLYLINE",
                        }
                    ],
                },
            )
        )
        if text_values is not None:
            ds = self.add_text_values(ds, text_values)
        if qualitative_evaluations is not None:
            ds = self.add_qualitative_evaluations(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)

    def add_volume_measurement(
        self,
        seg_dcm_file,
        dcm_file,
        volume_measurement,
        segment_number,
        graphic_data,
        finding,
        finding_site,
        tracking_id=None,
        tracking_uid=None,
        qualitative_evaluations=None,
        coded_values=None,
        text_values=None,
    ):
        """Add volume measurement

        Arguments:
            seg_dcm_file {[type]} -- [description]
            dcm_file {[type]} -- [description]
            volume_measurement {[type]} -- [description]
            segment_number {[type]} -- [description]
            graphic_data {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]

        Keyword Arguments:
            tracking_id {[type]} -- [description] (default: {None})
            tracking_uid {[type]} -- [description] (default: {None})
            qualitative_evaluations {[type]} -- [description] (default: {None})
            coded_values {[type]} -- [description] (default: {None})
            text_values {[type]} -- [description] (default: {None})
        """

        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        ds_ref_seg = dcmread(seg_dcm_file)
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        if coded_values is not None:
            ds = self.add_coded_values(ds, coded_values)
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "ReferencedSOPSequence": [
                        {
                            "ReferencedSOPClassUID": ds_ref_seg.SOPClassUID,
                            "ReferencedSOPInstanceUID": ds_ref_seg.SOPInstanceUID,
                            "ReferencedSegmentNumber": segment_number,
                        }
                    ],
                    "RelationshipType": "CONTAINS",
                    "ValueType": "IMAGE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121191",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Referenced Segment",
                        }
                    ],
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "UIDREF",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121232",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Source series for segmentation",
                        }
                    ],
                    "UID": ds_ref_seg.ReferencedSeriesSequence[0].SeriesInstanceUID,
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "118565006",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Volume",
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm3",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "cubic millimeter",
                                }
                            ],
                            "NumericValue": volume_measurement,
                        }
                    ],
                },
            )
        )
        if graphic_data is not None:
            ds_ref = dcmread(dcm_file)
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "CONTAINS",
                        "ValueType": "SCOORD",
                        "ConceptNameCodeSequence": [
                            {
                                "CodeValue": "111010",
                                "CodingSchemeDesignator": "DCM",
                                "CodeMeaning": "Center",
                            }
                        ],
                        "ContentSequence": [
                            {
                                "ReferencedSOPSequence": [
                                    {
                                        "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                        "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                    }
                                ],
                                "RelationshipType": "SELECTED FROM",
                                "ValueType": "IMAGE",  # value type
                            }
                        ],
                        "GraphicData": graphic_data,
                        "GraphicType": "POINT",
                    },
                )
            )
        if text_values is not None:
            ds = self.add_text_values(ds, text_values)
        if qualitative_evaluations is not None:
            ds = self.add_qualitative_evaluations(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)

    def add_volume_and_linear_measurement_single_axis(
        self,
        seg_dcm_file,
        dcm_file,
        volume_measurement,
        segment_number,
        graphic_data_center,
        linear_measurement,
        graphic_data_linear_measurement,
        measurement_type,
        finding,
        finding_site,
        tracking_id=None,
        tracking_uid=None,
        qualitative_evaluations=None,
        coded_values=None,
        text_values=None,
    ):
        """Add volume measurement with a single axis distance measurement

        Arguments:
            seg_dcm_file {[type]} -- [description]
            dcm_file {[type]} -- [description]
            volume_measurement {[type]} -- [description]
            segment_number {[type]} -- [description]
            graphic_data {[type]} -- [description]
            finding {[type]} -- [description]
            finding_site {[type]} -- [description]

        Keyword Arguments:
            tracking_id {[type]} -- [description] (default: {None})
            tracking_uid {[type]} -- [description] (default: {None})
            qualitative_evaluations {[type]} -- [description] (default: {None})
            coded_values {[type]} -- [description] (default: {None})
            text_values {[type]} -- [description] (default: {None})
        """

        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        if not tracking_uid:
            tracking_uid = generate_uid()
        ds_ref_seg = dcmread(seg_dcm_file)
        ds_ref = dcmread(dcm_file)
        ds = self.initiate_measurement_group()
        ds.ContentSequence = self.initiate_content_sequence(
            tracking_id, tracking_uid, finding, finding_site
        )
        if coded_values is not None:
            ds = self.add_coded_values(ds, coded_values)
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "ReferencedSOPSequence": [
                        {
                            "ReferencedSOPClassUID": ds_ref_seg.SOPClassUID,
                            "ReferencedSOPInstanceUID": ds_ref_seg.SOPInstanceUID,
                            "ReferencedSegmentNumber": segment_number,
                        }
                    ],
                    "RelationshipType": "CONTAINS",
                    "ValueType": "IMAGE",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121191",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Referenced Segment",
                        }
                    ],
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "UIDREF",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "121232",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Source series for segmentation",
                        }
                    ],
                    "UID": ds_ref_seg.ReferencedSeriesSequence[0].SeriesInstanceUID,
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "118565006",
                            "CodingSchemeDesignator": "SCT",
                            "CodeMeaning": "Volume",
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm3",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "cubic millimeter",
                                }
                            ],
                            "NumericValue": volume_measurement,
                        }
                    ],
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "SCOORD",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": "111010",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Center",
                        }
                    ],
                    "ContentSequence": [
                        {
                            "ReferencedSOPSequence": [
                                {
                                    "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                    "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                }
                            ],
                            "RelationshipType": "SELECTED FROM",
                            "ValueType": "IMAGE",  # value type
                        }
                    ],
                    "GraphicData": graphic_data_center,
                    "GraphicType": "POINT",
                },
            )
        )
        ds.ContentSequence.append(
            update_and_insert_additional_DICOM_attributes_in_ds(
                Dataset(),
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "NUM",
                    "ConceptNameCodeSequence": [
                        {
                            "CodeValue": measurement_type[0],
                            "CodingSchemeDesignator": measurement_type[1],
                            "CodeMeaning": measurement_type[2],
                        }
                    ],
                    "MeasuredValueSequence": [
                        {
                            "MeasurementUnitsCodeSequence": [
                                {
                                    "CodeValue": "mm",
                                    "CodingSchemeDesignator": "UCUM",
                                    "CodeMeaning": "millimeter",
                                }
                            ],
                            "NumericValue": linear_measurement,
                        }
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "INFERRED FROM",
                            "ValueType": "SCOORD",
                            "ContentSequence": [
                                {
                                    "ReferencedSOPSequence": [
                                        {
                                            "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                            "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                                        }
                                    ],
                                    "RelationshipType": "SELECTED FROM",
                                    "ValueType": "IMAGE",  # value type
                                }
                            ],
                            "GraphicData": graphic_data_linear_measurement,
                            "GraphicType": "POLYLINE",
                        }
                    ],
                },
            )
        )
        if text_values is not None:
            ds = self.add_text_values(ds, text_values)
        if qualitative_evaluations is not None:
            ds = self.add_qualitative_evaluations(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)
