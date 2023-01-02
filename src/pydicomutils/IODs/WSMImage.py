import os
import numpy as np
import random
from datetime import datetime

from pydicom import Dataset, Sequence
from pydicom.uid import generate_uid

from .IOD import IOD, IODTypes
from .modules.general_modules import (
    CommonInstanceReferenceModule,
    FrameOfReferenceModule,
    AcquisitionContextModule,
)
from .modules.general_modules import (
    MultiFrameFunctionalGroupsModule,
    MultiFrameDimensionModule,
    SpecimenModule,
)
from .modules.specific_image_modules import (
    WholeSlideMicroscopySeriesModule,
    WholeSlideMicroscopyImageModule,
)
from .modules.specific_image_modules import OpticalPathModule
from .sequences.Sequences import generate_sequence
from ..external.icc_profiles.icc_profiles import get_sRGB_icc_profile


class WSMImage(IOD):
    """Implementation of the WSM Image IOD
    ----------
    """

    def __init__(self):
        super().__init__(IODTypes.WSMImage)

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
            wsm_specific_image_modules = [
                WholeSlideMicroscopySeriesModule(),
                FrameOfReferenceModule(),
                AcquisitionContextModule(),
                MultiFrameFunctionalGroupsModule(),
                MultiFrameDimensionModule(),
                SpecimenModule(),
                WholeSlideMicroscopyImageModule(),
                OpticalPathModule(),
            ]
            for module in wsm_specific_image_modules:
                module.copy_required_dicom_attributes(
                    dataset_to_copy_from, self.dataset
                )
                if include_optional:
                    module.copy_optional_dicom_attributes(
                        dataset_to_copy_from, self.dataset
                    )

    def initiate(self):
        """Initiate the IOD by setting some dummy values for required attributes"""
        super().initiate()
        del self.dataset.Laterality
        # Whole Slide Microscopy Series
        # Frame of reference module
        self.dataset.FrameOfReferenceUID = generate_uid()
        # Enhanced General Equipment module
        self.dataset.Manufacturer = "UNKNOWN"
        self.dataset.ManufacturerModelName = "UNKNOWN"
        self.dataset.DeviceSerialNumber = "00000001"
        self.dataset.SoftwareVersions = "0.0.1"
        # Image Pixel Module
        self.dataset.SamplesPerPixel = 1
        self.dataset.PhotometricInterpretation = "MONOCHROME2"
        self.dataset.Rows = 256
        self.dataset.Columns = 256
        self.dataset.BitsAllocated = 8
        self.dataset.BitsStored = 8
        self.dataset.HighBit = 7
        self.dataset.PixelRepresentation = 0
        self.dataset.PixelData = np.random.randint(
            0, high=255, size=(256, 256), dtype=np.uint8
        ).tobytes()
        # Acquisition Context Module
        # Multi-frame Functional Groups Module
        self.dataset.SharedFunctionalGroupsSequence = generate_sequence(
            "SharedFunctionalGroupsSequence",
            [
                {
                    "PixelMeasuresSequence": [
                        {"SliceThickness": 1.0, "PixelSpacing": [0.001, 0.001]}
                    ],
                    "OpticalPathIdentificationSequence": [
                        {"OpticalPathIdentifier": "1"}
                    ],
                    "WholeSlideMicroscopyImageFrameTypeSequence": [
                        {"FrameType": ["DERIVED", "PRIMARY", "VOLUME", "NONE"]}
                    ],
                }
            ],
        )
        self.dataset.PerFrameFunctionalGroupsSequence = generate_sequence(
            "PerFrameFunctionalGroupsSequence",
            [
                {
                    "PlanePositionSlideSequence": [
                        {
                            "XOffsetInSlideCoordinateSystem": 0.0,
                            "YOffsetInSlideCoordinateSystem": 0.0,
                            "ZOffsetInSlideCoordinateSystem": 0.0,
                            "ColumnPositionInTotalImagePixelMatrix": 1,
                            "RowPositionInTotalImagePixelMatrix": 1,
                        }
                    ]
                }
            ],
        )
        # Multi-frame Dimension Module
        self.dataset.DimensionOrganizationSequence = generate_sequence(
            "DimensionOrganizationSequence",
            [{"DimensionOrganizationUID": generate_uid()}],
        )
        self.dataset.DimensionOrganizationType = "TILED_SPARSE"
        self.dataset.DimensionIndexSequence = generate_sequence(
            "DimensionIndexSequence",
            [
                {
                    "DimensionIndexPointer": 0x00480106,
                    "FunctionalGroupPointer": 0x00480105,
                    "DimensionOrganizationUID": self.dataset.DimensionOrganizationSequence[
                        0
                    ].DimensionOrganizationUID,
                }
            ],
        )
        # Specimen Module
        self.dataset.ContainerIdentifier = "".join(
            random.choice("0123456789ABCDEF") for i in range(16)
        )
        self.dataset.SpecimenDescriptionSequence = generate_sequence(
            "SpecimenDescriptionSequence",
            [
                {
                    "SpecimenIdentifier": "".join(
                        random.choice("0123456789ABCDEF") for i in range(16)
                    ),
                    "SpecimenUID": generate_uid(),
                    "IssuerOfTheSpecimenIdentifierSequence": [],
                    "SpecimenPreparationSequence": [],
                }
            ],
        )
        # Whole Slide Microscopy Image Module
        self.dataset.ImageType = ["DERIVED", "PRIMARY", "VOLUME", "NONE"]
        self.dataset.ImagedVolumeWidth = 0.256
        self.dataset.ImagedVolumeHeight = 0.256
        self.dataset.ImagedVolumeDepth = 1.0
        self.dataset.TotalPixelMatrixColumns = 256
        self.dataset.TotalPixelMatrixRows = 256
        self.dataset.TotalPixelMatrixFocalPlanes = 1
        self.dataset.TotalPixelMatrixOriginSequence = generate_sequence(
            "TotalPixelMatrixOriginSequence",
            [
                {
                    "XOffsetInSlideCoordinateSystem": "0.0",
                    "YOffsetInSlideCoordinateSystem": "0.0",
                }
            ],
        )
        self.dataset.ImageOrientationSlide = ["1.0", "0.0", "0.0", "0.0", "1.0", "0.0"]
        self.dataset.SamplesPerPixel = 1
        self.dataset.PhotometricInterpretation = "MONOCHROME2"
        self.dataset.NumberOfFrames = 1
        self.dataset.BitsAllocated = 8
        self.dataset.BitsStored = 8
        self.dataset.HighBit = 7
        self.dataset.PixelRepresentation = 0
        self.dataset.AcquisitionDateTime = datetime.now().strftime("%Y%m%d%H%M%S")
        self.dataset.AcquisitionDuration = 1.0
        self.dataset.LossyImageCompression = "00"
        self.dataset.PresentationLUTShape = "IDENTITY"
        self.dataset.RescaleIntercept = "0.0"
        self.dataset.RescaleSlope = "1.0"
        self.dataset.VolumetricProperties = "VOLUME"
        self.dataset.SpecimenLabelInImage = "NO"
        self.dataset.BurnedInAnnotation = "NO"
        self.dataset.FocusMethod = "AUTO"
        self.dataset.ExtendedDepthOfField = "NO"
        # Optical Path
        self.dataset.NumberOfOpticalPaths = 1
        self.dataset.OpticalPathSequence = generate_sequence(
            "OpticalPathSequence",
            [
                {
                    "OpticalPathIdentifier": "1",
                    "IlluminationColorCodeSequence": [
                        {
                            "CodeValue": "R-102CO",
                            "CodingSchemeDesignator": "SRT",
                            "CodeMeaning": "Full Spectrum",
                        }
                    ],
                    "IlluminationTypeCodeSequence": [
                        {
                            "CodeValue": "111741",
                            "CodingSchemeDesignator": "DCM",
                            "CodeMeaning": "Transmission illumination",
                        }
                    ],
                }
            ],
        )

    def add_pixel_data(
        self,
        pixel_array,
        photometric_interpretation="MONOCHROME2",
        pixel_spacing=None,
        slice_thickness=None,
        tile_size=None,
    ):
        """Add pixel data

        Arguments:
            pixel_array {2D/3D np.array} -- The pixel data to add to the WSM object

        Keyword Arguments:
            photometric_interpretation {str} -- Photometric interpretation of the provided pixel_array (default: {"MONOCHROME2"})
            pixel_spacing {[str str]} -- Pixel spacing of the provided pixel_array (default: {None})
            slice_thickness {str} -- Slice thickness of the provided pixel_array (default: {None})
            tile_size {(int, int)} -- Tile size to apply when tiling the proived pixel_array (default: {None})
        """
        if (
            photometric_interpretation != "MONOCHROME2"
            and photometric_interpretation != "RGB"
        ):
            print("Unsupported PhotometricInterpretation", photometric_interpretation)
            return
        if len(pixel_array.shape) != 2 and photometric_interpretation == "MONOCHROME2":
            print(
                "Unsupported number of samples per pixel",
                pixel_array.shape[2],
                "only one sample per pixel is supported for MONOCHROME2",
            )
            return
        if (
            len(pixel_array.shape) != 3
            and photometric_interpretation == "RGB"
            and pixel_array.shape[2] != 3
        ):
            print(
                "Unsupported number of samples per pixel",
                pixel_array.shape[2],
                "only three samples per pixel is supported for RGB",
            )
            return
        if photometric_interpretation == "MONOCHROME2":
            self.dataset.SamplesPerPixel = 1
        else:
            self.dataset.SamplesPerPixel = 3
            self.dataset.PlanarConfiguration = 0
            del self.dataset.PresentationLUTShape
            del self.dataset.RescaleIntercept
            del self.dataset.RescaleSlope
            self.dataset.OpticalPathSequence[0].ICCProfile = get_sRGB_icc_profile()
        if pixel_spacing is None:
            pixel_spacing = [1.0, 1.0]
        if slice_thickness is None:
            slice_thickness = 1.0
        if tile_size is None:
            tile_size = pixel_array.shape[0:2]
        self.dataset.PhotometricInterpretation = photometric_interpretation
        self.dataset.Rows = tile_size[0]
        self.dataset.Columns = tile_size[1]
        if pixel_array.dtype == "uint8":
            self.dataset.BitsAllocated = 8
            self.dataset.BitsStored = 8
            self.dataset.HighBit = 7
            self.dataset.PixelRepresentation = 0
        elif pixel_array.dtype == "uint16":
            self.dataset.BitsAllocated = 16
            self.dataset.BitsStored = 16
            self.dataset.HighBit = 15
            self.dataset.PixelRepresentation = 0
        else:
            print(
                "Unsupported pixel type",
                pixel_array.dtype,
                "only uint8 and uint16 is supported",
            )
        self.dataset.ImagedVolumeWidth = pixel_array.shape[1] * pixel_spacing[1]
        self.dataset.ImagedVolumeHeight = pixel_array.shape[0] * pixel_spacing[0]
        self.dataset.ImagedVolumeDepth = slice_thickness
        self.dataset.TotalPixelMatrixColumns = pixel_array.shape[1]
        self.dataset.TotalPixelMatrixRows = pixel_array.shape[0]
        self.dataset.SharedFunctionalGroupsSequence = generate_sequence(
            "SharedFunctionalGroupsSequence",
            [
                {
                    "PixelMeasuresSequence": [
                        {
                            "SliceThickness": slice_thickness,
                            "PixelSpacing": pixel_spacing,
                        }
                    ],
                    "OpticalPathIdentificationSequence": [
                        {"OpticalPathIdentifier": "1"}
                    ],
                    "WholeSlideMicroscopyImageFrameTypeSequence": [
                        {"FrameType": ["DERIVED", "PRIMARY", "VOLUME", "NONE"]}
                    ],
                }
            ],
        )
        if (
            tile_size[0] == pixel_array.shape[0]
            and tile_size[1] == pixel_array.shape[1]
        ):
            self.dataset.PixelData = pixel_array.tobytes()
        else:
            if len(pixel_array.shape) == 2:
                pixel_array = np.expand_dims(pixel_array, axis=2)
            byte_array = None
            per_frame_function_groups_sequence_data = list()
            number_of_frames = 0
            number_row_tiles = int(np.ceil(pixel_array.shape[0] / tile_size[0]))
            number_col_tiles = int(np.ceil(pixel_array.shape[1] / tile_size[1]))
            for row_ind in range(0, number_row_tiles):
                row_array = pixel_array[
                    row_ind
                    * tile_size[0] : min(
                        (row_ind + 1) * tile_size[0], pixel_array.shape[0]
                    ),
                    :,
                    :,
                ]
                for col_ind in range(0, number_col_tiles):
                    tile = row_array[
                        :,
                        col_ind
                        * tile_size[1] : min(
                            (col_ind + 1) * tile_size[1], pixel_array.shape[1]
                        ),
                        :,
                    ]
                    tile = np.pad(
                        tile,
                        (
                            (0, tile_size[0] - tile.shape[0]),
                            (0, tile_size[1] - tile.shape[1]),
                            (0, 0),
                        ),
                        constant_values=0,
                    )
                    if byte_array is None:
                        byte_array = tile.tobytes()
                    else:
                        byte_array = byte_array + tile.tobytes()
                    per_frame_function_groups_sequence_data.append(
                        {
                            "PlanePositionSlideSequence": [
                                {
                                    "XOffsetInSlideCoordinateSystem": float(
                                        str(col_ind * tile_size[0] * pixel_spacing[0])[
                                            0:16
                                        ]
                                    ),
                                    "YOffsetInSlideCoordinateSystem": float(
                                        str(col_ind * tile_size[1] * pixel_spacing[1])[
                                            0:16
                                        ]
                                    ),
                                    "ZOffsetInSlideCoordinateSystem": 0.0,
                                    "ColumnPositionInTotalImagePixelMatrix": col_ind
                                    * tile_size[1]
                                    + 1,
                                    "RowPositionInTotalImagePixelMatrix": row_ind
                                    * tile_size[0]
                                    + 1,
                                }
                            ]
                        }
                    )
                    number_of_frames += 1
            self.dataset.NumberOfFrames = number_of_frames
            self.dataset.PixelData = byte_array
            self.dataset.PerFrameFunctionalGroupsSequence = generate_sequence(
                "PerFrameFunctionalGroupsSequence",
                per_frame_function_groups_sequence_data,
            )
