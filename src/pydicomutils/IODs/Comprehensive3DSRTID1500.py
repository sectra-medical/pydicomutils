import random
from datetime import datetime
from pathlib import Path

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
from .sequences.Sequences import (
    generate_reference_sop_sequence_json,
    ConceptCodeSequenceItem,
    ConceptNameCodeSequenceItem,
)


class Comprehensive3DSRTID1500(IOD):
    """Implementation of Comprehensive 3D SR IOD class using TID 1500"""

    def __init__(self, referenced_dcms=None):
        # Initiate the IOD
        super().__init__(IODTypes.Comprehensive3DSR)
        # Create an empty IOD, i.e., add standard DICOM attributes but with no values
        super().create_empty_iod()
        # Add specific SR document modules and corresponding DICOM attributes
        self.copy_required_dicom_attributes(Dataset(), include_optional=True)

        # Start preparing the dataset for using TID 1500
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
        self.dataset.ValueType = "CONTAINER"
        self.dataset.ConceptNameCodeSequence = generate_sequence(
            "ConceptNameCodeSequence",
            [
                ConceptNameCodeSequenceItem(
                    "126000", "DCM", "Imaging Measurement Report"
                ).as_dict()
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
                        ConceptNameCodeSequenceItem(
                            "121049", "DCM", "Language of Content Item and Descendants"
                        ).as_dict()
                    ],
                    "ConceptCodeSequence": [
                        ConceptCodeSequenceItem("eng", "RFC5646", "English").as_dict()
                    ],
                    "ContentSequence": [
                        {
                            "RelationshipType": "HAS CONCEPT MOD",
                            "ValueType": "CODE",
                            "ConceptNameCodeSequence": [
                                ConceptNameCodeSequenceItem(
                                    "121046", "DCM", "Country of Language"
                                ).as_dict()
                            ],
                            "ConceptCodeSequence": [
                                ConceptCodeSequenceItem(
                                    "US", "ISO3166_1", "United States"
                                ).as_dict()
                            ],
                        }
                    ],
                },
                {
                    "RelationshipType": "HAS CONCEPT MOD",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "121058", "DCM", "Procedure Reported"
                        ).as_dict()
                    ],
                    "ConceptCodeSequence": [
                        ConceptCodeSequenceItem(
                            "363679005", "SCT", "Imaging Procedure"
                        ).as_dict()
                    ],
                },
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CONTAINER",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "111028", "DCM", "Image Library"
                        ).as_dict()
                    ],
                    "ContinuityOfContent": "SEPARATE",
                    "ContentSequence": [
                        {
                            "RelationshipType": "CONTAINS",
                            "ValueType": "CONTAINER",
                            "ConceptNameCodeSequence": [
                                ConceptNameCodeSequenceItem(
                                    "126200", "DCM", "Image Library Group"
                                ).as_dict()
                            ],
                            "ContinuityOfContent": "SEPARATE",
                            "ContentSequence": [],
                        }
                    ],
                },
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CONTAINER",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "126010", "DCM", "Imaging Measurements"
                        ).as_dict()
                    ],
                    "ContinuityOfContent": "SEPARATE",
                    "ContentSequence": [],
                },
            ],
        )

        if referenced_dcms:
            self.__initiate__(referenced_dcms)

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

    def __initiate__(self, referenced_dcms=None):
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

        self.dataset.ContentSequence[2].ContentSequence[0].ContentSequence = (
            generate_sequence(
                "ContentSequence",
                [
                    generate_reference_sop_sequence_json(dcm_file)
                    for dcm_file in referenced_dcms
                ],
            )
        )

    def __initiate_measurement_group__(
        self,
        template_id: str,
        tracking_id: str = None,
        tracking_uid: str = None,
        finding_category: ConceptCodeSequenceItem = None,
        finding_type: ConceptCodeSequenceItem = None,
        finding_site: ConceptCodeSequenceItem = None,
    ):
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
                ConceptNameCodeSequenceItem(
                    "125007", "DCM", "Measurement Group"
                ).as_dict()
            ],
        )
        ds.ContentTemplateSequence = generate_sequence(
            "ContentTemplateSequence",
            [
                {
                    "MappingResource": "DCMR",
                    "MappingResourceUID": "1.2.840.10008.8.1.1",
                    "TemplateIdentifier": template_id,
                }
            ],
        )
        ds.ContinuityOfContent = "SEPARATE"
        content_sequence = []
        if tracking_id is not None:
            content_sequence.append(
                {
                    "RelationshipType": "HAS OBS CONTEXT",
                    "ValueType": "TEXT",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "112039", "DCM", "Tracking Identifier"
                        ).as_dict()
                    ],
                    "TextValue": tracking_id,
                }
            )
        if tracking_uid is not None:
            content_sequence.append(
                {
                    "RelationshipType": "HAS OBS CONTEXT",
                    "ValueType": "UIDREF",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "112040", "DCM", "Tracking Unique Identifier"
                        ).as_dict()
                    ],
                    "UID": tracking_uid,
                }
            )
        if finding_category is not None:
            content_sequence.append(
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "276214006", "SCT", "Finding category"
                        ).as_dict()
                    ],
                    "ConceptCodeSequence": [
                        finding_category.as_dict(),
                    ],
                }
            )
        if finding_type is not None:
            content_sequence.append(
                {
                    "RelationshipType": "CONTAINS",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "121071", "DCM", "Finding"
                        ).as_dict()
                    ],
                    "ConceptCodeSequence": [
                        finding_type.as_dict(),
                    ],
                }
            )
        if finding_site is not None:
            content_sequence.append(
                {
                    "RelationshipType": "HAS CONCEPT MOD",
                    "ValueType": "CODE",
                    "ConceptNameCodeSequence": [
                        ConceptNameCodeSequenceItem(
                            "363698007", "SCT", "Finding Site"
                        ).as_dict()
                    ],
                    "ConceptCodeSequence": [
                        finding_site.as_dict(),
                    ],
                }
            )
        ds.ContentSequence = generate_sequence(
            "ContentSequence",
            content_sequence,
        )

        return ds

    def __add_qualitative_evaluations__(self, ds, qualitative_evaluations):
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
                                ConceptNameCodeSequenceItem(
                                    "C00034375", "UMLS", "Qualitative Evaluations"
                                ).as_dict()
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
                                ConceptNameCodeSequenceItem(
                                    "C00034375", "UMLS", "Qualitative Evaluations"
                                ).as_dict()
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

    def __add_coded_values__(self, ds, coded_values):
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

    def __handle_tracking_id__(self, tracking_id):
        if not tracking_id:
            tracking_id = "".join(random.choice("0123456789ABCDEF") for i in range(16))
        return tracking_id

    def __handle_tracking_uid__(self, tracking_uid):
        if not tracking_uid:
            tracking_uid = generate_uid()
        return tracking_uid

    def __get_dataset_from_dcm_file__(self, dcm_file):
        if isinstance(dcm_file, str) or isinstance(dcm_file, Path):
            return dcmread(dcm_file)
        return dcm_file

    def add_qualitative_finding(
        self,
        dcm_file,
        finding_type,
        tracking_id=None,
        tracking_uid=None,
        finding_category=None,
        finding_site=None,
        location_data=None,
        location_type=None,
        contour_data=None,
        contour_type=None,
        qualitative_evaluations=None,
        coded_values=None,
    ):
        """Add qualitative finding, without location, with location or with region as given by a contour

        Arguments:
            dcm_file {Path or Dataset} -- Path or Dataset of the DICOM file that will be referenced
            finding_type {ConceptCodeSequenceItem} -- Concept code sequence item of the specific finding type
            tracking_id {str} -- Tracking ID (default: {None})
            tracking_uid {str} -- Tracking UID (default: {None})
            finding_category {ConceptCodeSequenceItem} -- Concept code sequence item of the general finding category (default: {None})
            finding_site {ConceptCodeSequenceItem} -- Concept code sequence item of the finding site (default: {None})
            location_data {list} -- List of location data points
            location_type {str} -- Type of location data points, e.g. "POINT", "POLYLINE", "CIRCLE", or "ELLIPSE"
            contour_data {list} -- List of contour data points
            contour_type {str} -- Type of contour data points, e.g. "POLYLINE", "CIRCLE", or "ELLIPSE"
            qualitative_evaluations {list} -- List of qualitative evaluations (default: {None})
            coded_values {list} -- List of coded values (default: {None})
        """
        # Handle tracking ID and UID
        tracking_id = self.__handle_tracking_id__(tracking_id)
        tracking_uid = self.__handle_tracking_uid__(tracking_uid)
        # Get the dataset from the DICOM file
        ds_ref = self.__get_dataset_from_dcm_file__(dcm_file)
        # Ensure that either location data or contour data is provided, not both
        if location_data is not None and contour_data is not None:
            raise ValueError(
                "Either location data or contour data should be provided, not both."
            )
        # Set template ID depending on using contour data or not
        template_id = "1501" if contour_data is None else "1410"
        # Initiate the measurement group with relevant template ID
        # and the essential attributes
        ds = self.__initiate_measurement_group__(
            template_id,
            tracking_id=tracking_id,
            tracking_uid=tracking_uid,
            finding_type=finding_type,
            finding_category=finding_category,
            finding_site=finding_site,
        )
        if location_data is None and contour_data is None:
            # Set the image reference as given by the SOP Instance UID in the DICOM file
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "CONTAINS",
                        "ValueType": "IMAGE",
                        "ReferencedSOPSequence": [
                            {
                                "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID,
                            }
                        ],
                    },
                )
            )
        elif location_data is not None and contour_data is None:
            # Set the location using the providing location data and type and assuming the location is for the
            # referenced image as given by the SOP Instance UID in the DICOM file
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "CONTAINS",
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
                                "ValueType": "IMAGE",
                            }
                        ],
                        "GraphicData": location_data,
                        "GraphicType": location_type,
                    },
                )
            )
        elif location_data is None and contour_data is not None:
            # Set the region using the providing contour data and type and assuming the contour is for the
            # referenced image as given by the SOP Instance UID in the DICOM file
            ds.ContentSequence.append(
                update_and_insert_additional_DICOM_attributes_in_ds(
                    Dataset(),
                    {
                        "RelationshipType": "CONTAINS",
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
                                "ValueType": "IMAGE",
                            }
                        ],
                        "GraphicData": contour_data,
                        "GraphicType": contour_type,
                    },
                )
            )
        # Add coded value and qualitative evaluations if provided
        if coded_values is not None:
            ds = self.__add_coded_values__(ds, coded_values)
        if qualitative_evaluations is not None:
            ds = self.__add_qualitative_evaluations__(ds, qualitative_evaluations)
        self.dataset.ContentSequence[3].ContentSequence.append(ds)
