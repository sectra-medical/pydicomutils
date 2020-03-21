import numpy as np
import random
from datetime import datetime

from pydicom import Dataset, Sequence
from pydicom.uid import generate_uid

from .IOD import IOD, IODTypes
from .modules.general_modules import CommonInstanceReferenceModule, FrameOfReferenceModule, AcquisitionContextModule
from .modules.general_modules import MultiFrameFunctionalGroupsModule, MultiFrameDimensionModule, SpecimenModule
from .modules.specific_image_modules import WholeSlideMicroscopySeriesModule, WholeSlideMicroscopyImageModule 
from .modules.specific_image_modules import OpticalPathModule
from .sequences.Sequences import generate_sequence

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
            wsm_specific_image_modules = [WholeSlideMicroscopySeriesModule(), FrameOfReferenceModule(), AcquisitionContextModule(), 
                                          MultiFrameFunctionalGroupsModule(), MultiFrameDimensionModule(), SpecimenModule(), 
                                          WholeSlideMicroscopyImageModule(), OpticalPathModule()]
            for module in wsm_specific_image_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                    self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                        self.dataset)
    
    def initiate(self):
        """Initiate the IOD by setting some dummy values for required attributes
        """
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
        self.dataset.PixelData = np.random.randint(0,high=255,size=(256,256), dtype=np.uint8).tobytes()
        # Acquisition Context Module
        # Multi-frame Functional Groups Module
        self.dataset.SharedFunctionalGroupsSequence = generate_sequence("SharedFunctionalGroupsSequence", [
            {
                "PixelMeasuresSequence": [
                    {
                        "SliceThickness": 1.0,
                        "PixelSpacing": [0.001, 0.001]
                    }
                ],
                "OpticalPathIdentificationSequence": [
                    {
                        "OpticalPathIdentifier": "1"
                    }
                ],
                "WholeSlideMicroscopyImageFrameTypeSequence": [
                    {
                        "FrameType": ["DERIVED", "PRIMARY", "VOLUME", "NONE"]
                    }
                ]
            }
        ])
        
        self.dataset.PerFrameFunctionalGroupsSequence = generate_sequence("PerFrameFunctionalGroupsSequence", [
            {
                "PlanePositionSlideSequence": [
                    {
                        "XOffsetInSlideCoordinateSystem": 0.0,
                        "YOffsetInSlideCoordinateSystem": 0.0,
                        "ZOffsetInSlideCoordinateSystem": 0.0,
                        "ColumnPositionInTotalImagePixelMatrix": 1, 
                        "RowPositionInTotalImagePixelMatrix": 1
                    }
                ]
            }
        ])
        # Multi-frame Dimension Module
        self.dataset.DimensionOrganizationSequence = generate_sequence("DimensionOrganizationSequence", [
            {
                "DimensionOrganizationUID": generate_uid()
            }
        ])
        self.dataset.DimensionOrganizationType = "TILED_SPARSE"
        self.dataset.DimensionIndexSequence = generate_sequence("DimensionIndexSequence", [
            {
                "DimensionIndexPointer": 0x00480106,
                "FunctionalGroupPointer": 0x00480105,
                "DimensionOrganizationUID": self.dataset.DimensionOrganizationSequence[0].DimensionOrganizationUID
            }
        ])
        # Specimen Module
        self.dataset.ContainerIdentifier = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        self.dataset.SpecimenDescriptionSequence = generate_sequence("SpecimenDescriptionSequence", [
            {
                "SpecimenIdentifier": ''.join(random.choice('0123456789ABCDEF') for i in range(16)),
                "SpecimenUID": generate_uid(),
                "IssuerOfTheSpecimenIdentifierSequence": [],
                "SpecimenPreparationSequence": []
            }
        ])
        # Whole Slide Microscopy Image Module
        self.dataset.ImageType = ["DERIVED", "PRIMARY", "VOLUME", "NONE"]
        self.dataset.ImagedVolumeWidth = 0.256
        self.dataset.ImagedVolumeHeight = 0.256
        self.dataset.ImagedVolumeDepth = 1.0
        self.dataset.TotalPixelMatrixColumns = 256
        self.dataset.TotalPixelMatrixRows = 256
        self.dataset.TotalPixelMatrixFocalPlanes = 1
        self.dataset.TotalPixelMatrixOriginSequence = generate_sequence("TotalPixelMatrixOriginSequence", [
            {
                "XOffsetInSlideCoordinateSystem": "0.0",
                "YOffsetInSlideCoordinateSystem": "0.0"
            }
        ])
        self.dataset.ImageOrientationSlide = ["1.0", "0.0","0.0", "0.0", "1.0", "0.0"]
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
        self.dataset.OpticalPathSequence = generate_sequence("OpticalPathSequence", [
            {
                "OpticalPathIdentifier": "1",
                "IlluminationColorCodeSequence": [
                    {
                        "CodeValue": "R-102CO",
                        "CodingSchemeDesignator": "SRT",
                        "CodeMeaning": "Full Spectrum"
                    }
                ],
                "IlluminationTypeCodeSequence": [
                    {
                        "CodeValue": "111741",
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": "Transmission illumination"
                    }
                ]
            }
        ])


    def add_pixel_data(self, pixel_array,
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
        if photometric_interpretation != "MONOCHROME2" and photometric_interpretation != "RGB":
            print("Unsupported PhotometricInterpretation", photometric_interpretation)
            return
        if len(pixel_array.shape) != 2 and photometric_interpretation == "MONOCHROME2":
            print("Unsupported number of samples per pixel",pixel_array.shape[2],
                  "only one sample per pixel is supported for MONOCHROME2")
            return
        if len(pixel_array.shape) != 3 and photometric_interpretation == "RGB" and pixel_array.shape[2] != 3:
            print("Unsupported number of samples per pixel", pixel_array.shape[2],
                  "only three samples per pixel is supported for RGB")
            return
        if photometric_interpretation == "MONOCHROME2":
            self.dataset.SamplesPerPixel = 1
        else:
            self.dataset.SamplesPerPixel = 3
            self.dataset.PlanarConfiguration = 0
            del self.dataset.PresentationLUTShape
            del self.dataset.RescaleIntercept
            del self.dataset.RescaleSlope
            self.dataset.OpticalPathSequence[0].ICCProfile = get_rgb_icc_profile()
        if pixel_spacing is None:
            pixel_spacing = [1.0, 1.0]
        if slice_thickness is None:
            slice_thickness = 1.0
        if tile_size is None:
            tile_size = pixel_array.shape[0:2]
        self.dataset.PhotometricInterpretation = photometric_interpretation
        self.dataset.Rows = tile_size[1]
        self.dataset.Columns = tile_size[0]
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
            print("Unsupported pixel type",pixel_array.dtype,
                  "only uint8 and uint16 is supported")
        self.dataset.ImagedVolumeWidth = pixel_array.shape[0] * pixel_spacing[0]
        self.dataset.ImagedVolumeHeight = pixel_array.shape[1] * pixel_spacing[1]
        self.dataset.ImagedVolumeDepth = slice_thickness
        self.dataset.TotalPixelMatrixColumns = pixel_array.shape[0]
        self.dataset.TotalPixelMatrixRows = pixel_array.shape[1]
        self.dataset.SharedFunctionalGroupsSequence = generate_sequence("SharedFunctionalGroupsSequence", [
            {
                "PixelMeasuresSequence": [
                    {
                        "SliceThickness": slice_thickness,
                        "PixelSpacing": pixel_spacing
                    }
                ],
                "OpticalPathIdentificationSequence": [
                    {
                        "OpticalPathIdentifier": "1"
                    }
                ],
                "WholeSlideMicroscopyImageFrameTypeSequence": [
                    {
                        "FrameType": ["DERIVED", "PRIMARY", "VOLUME", "NONE"]
                    }
                ]
            }
        ])
        if tile_size[0] == pixel_array.shape[0] and tile_size[1] == pixel_array.shape[1]:
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
                row_array = pixel_array[row_ind * tile_size[0]:min((row_ind + 1) * tile_size[0], pixel_array.shape[0]),:,:]
                for col_ind in range(0, number_col_tiles):
                    tile = row_array[:,col_ind * tile_size[1]:min((col_ind + 1) * tile_size[1], pixel_array.shape[1]),:]
                    tile = np.pad(tile, ((0,tile_size[0]-tile.shape[0]),(0,tile_size[1]-tile.shape[1]),(0,0)), constant_values=0)
                    if byte_array is None:
                        byte_array = tile.tobytes()
                    else:
                        byte_array = byte_array + tile.tobytes()
                    per_frame_function_groups_sequence_data.append(
                        {
                            "PlanePositionSlideSequence": [
                                {
                                    "XOffsetInSlideCoordinateSystem": col_ind * tile_size[0] * pixel_spacing[0],
                                    "YOffsetInSlideCoordinateSystem": col_ind * tile_size[1] * pixel_spacing[1],
                                    "ZOffsetInSlideCoordinateSystem": 0.0,
                                    "ColumnPositionInTotalImagePixelMatrix": col_ind * tile_size[0] + 1, 
                                    "RowPositionInTotalImagePixelMatrix": row_ind * tile_size[1] + 1
                                }
                            ]
                        }
                    )
                    number_of_frames += 1
            self.dataset.NumberOfFrames = number_of_frames
            self.dataset.PixelData = byte_array
            self.dataset.PerFrameFunctionalGroupsSequence = generate_sequence("PerFrameFunctionalGroupsSequence", 
                                                                              per_frame_function_groups_sequence_data)

def get_rgb_icc_profile():
    return b'\x00\x00\x0cHLino\x02\x10\x00\x00mntrRGB XYZ \x07\xce\x00\x02\x00\t\x00\x06\x001\x00\x00acspMSFT\x00\x00\x00\x00IEC sRGB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf6\xd6\x00\x01\x00\x00\x00\x00\xd3-HP  \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11cprt\x00\x00\x01P\x00\x00\x003desc\x00\x00\x01\x84\x00\x00\x00lwtpt\x00\x00\x01\xf0\x00\x00\x00\x14bkpt\x00\x00\x02\x04\x00\x00\x00\x14rXYZ\x00\x00\x02\x18\x00\x00\x00\x14gXYZ\x00\x00\x02,\x00\x00\x00\x14bXYZ\x00\x00\x02@\x00\x00\x00\x14dmnd\x00\x00\x02T\x00\x00\x00pdmdd\x00\x00\x02\xc4\x00\x00\x00\x88vued\x00\x00\x03L\x00\x00\x00\x86view\x00\x00\x03\xd4\x00\x00\x00$lumi\x00\x00\x03\xf8\x00\x00\x00\x14meas\x00\x00\x04\x0c\x00\x00\x00$tech\x00\x00\x040\x00\x00\x00\x0crTRC\x00\x00\x04<\x00\x00\x08\x0cgTRC\x00\x00\x04<\x00\x00\x08\x0cbTRC\x00\x00\x04<\x00\x00\x08\x0ctext\x00\x00\x00\x00Copyright (c) 1998 Hewlett-Packard Company\x00\x00desc\x00\x00\x00\x00\x00\x00\x00\x12sRGB IEC61966-2.1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12sRGB IEC61966-2.1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00XYZ \x00\x00\x00\x00\x00\x00\xf3Q\x00\x01\x00\x00\x00\x01\x16\xccXYZ \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00XYZ \x00\x00\x00\x00\x00\x00o\xa2\x00\x008\xf5\x00\x00\x03\x90XYZ \x00\x00\x00\x00\x00\x00b\x99\x00\x00\xb7\x85\x00\x00\x18\xdaXYZ \x00\x00\x00\x00\x00\x00$\xa0\x00\x00\x0f\x84\x00\x00\xb6\xcfdesc\x00\x00\x00\x00\x00\x00\x00\x16IEC http://www.iec.ch\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16IEC http://www.iec.ch\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00desc\x00\x00\x00\x00\x00\x00\x00.IEC 61966-2.1 Default RGB colour space - sRGB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00.IEC 61966-2.1 Default RGB colour space - sRGB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00desc\x00\x00\x00\x00\x00\x00\x00,Reference Viewing Condition in IEC61966-2.1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,Reference Viewing Condition in IEC61966-2.1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00view\x00\x00\x00\x00\x00\x13\xa4\xfe\x00\x14_.\x00\x10\xcf\x14\x00\x03\xed\xcc\x00\x04\x13\x0b\x00\x03\\\x9e\x00\x00\x00\x01XYZ \x00\x00\x00\x00\x00L\tV\x00P\x00\x00\x00W\x1f\xe7meas\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x8f\x00\x00\x00\x02sig \x00\x00\x00\x00CRT curv\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x05\x00\n\x00\x0f\x00\x14\x00\x19\x00\x1e\x00#\x00(\x00-\x002\x007\x00;\x00@\x00E\x00J\x00O\x00T\x00Y\x00^\x00c\x00h\x00m\x00r\x00w\x00|\x00\x81\x00\x86\x00\x8b\x00\x90\x00\x95\x00\x9a\x00\x9f\x00\xa4\x00\xa9\x00\xae\x00\xb2\x00\xb7\x00\xbc\x00\xc1\x00\xc6\x00\xcb\x00\xd0\x00\xd5\x00\xdb\x00\xe0\x00\xe5\x00\xeb\x00\xf0\x00\xf6\x00\xfb\x01\x01\x01\x07\x01\r\x01\x13\x01\x19\x01\x1f\x01%\x01+\x012\x018\x01>\x01E\x01L\x01R\x01Y\x01`\x01g\x01n\x01u\x01|\x01\x83\x01\x8b\x01\x92\x01\x9a\x01\xa1\x01\xa9\x01\xb1\x01\xb9\x01\xc1\x01\xc9\x01\xd1\x01\xd9\x01\xe1\x01\xe9\x01\xf2\x01\xfa\x02\x03\x02\x0c\x02\x14\x02\x1d\x02&\x02/\x028\x02A\x02K\x02T\x02]\x02g\x02q\x02z\x02\x84\x02\x8e\x02\x98\x02\xa2\x02\xac\x02\xb6\x02\xc1\x02\xcb\x02\xd5\x02\xe0\x02\xeb\x02\xf5\x03\x00\x03\x0b\x03\x16\x03!\x03-\x038\x03C\x03O\x03Z\x03f\x03r\x03~\x03\x8a\x03\x96\x03\xa2\x03\xae\x03\xba\x03\xc7\x03\xd3\x03\xe0\x03\xec\x03\xf9\x04\x06\x04\x13\x04 \x04-\x04;\x04H\x04U\x04c\x04q\x04~\x04\x8c\x04\x9a\x04\xa8\x04\xb6\x04\xc4\x04\xd3\x04\xe1\x04\xf0\x04\xfe\x05\r\x05\x1c\x05+\x05:\x05I\x05X\x05g\x05w\x05\x86\x05\x96\x05\xa6\x05\xb5\x05\xc5\x05\xd5\x05\xe5\x05\xf6\x06\x06\x06\x16\x06\'\x067\x06H\x06Y\x06j\x06{\x06\x8c\x06\x9d\x06\xaf\x06\xc0\x06\xd1\x06\xe3\x06\xf5\x07\x07\x07\x19\x07+\x07=\x07O\x07a\x07t\x07\x86\x07\x99\x07\xac\x07\xbf\x07\xd2\x07\xe5\x07\xf8\x08\x0b\x08\x1f\x082\x08F\x08Z\x08n\x08\x82\x08\x96\x08\xaa\x08\xbe\x08\xd2\x08\xe7\x08\xfb\t\x10\t%\t:\tO\td\ty\t\x8f\t\xa4\t\xba\t\xcf\t\xe5\t\xfb\n\x11\n\'\n=\nT\nj\n\x81\n\x98\n\xae\n\xc5\n\xdc\n\xf3\x0b\x0b\x0b"\x0b9\x0bQ\x0bi\x0b\x80\x0b\x98\x0b\xb0\x0b\xc8\x0b\xe1\x0b\xf9\x0c\x12\x0c*\x0cC\x0c\\\x0cu\x0c\x8e\x0c\xa7\x0c\xc0\x0c\xd9\x0c\xf3\r\r\r&\r@\rZ\rt\r\x8e\r\xa9\r\xc3\r\xde\r\xf8\x0e\x13\x0e.\x0eI\x0ed\x0e\x7f\x0e\x9b\x0e\xb6\x0e\xd2\x0e\xee\x0f\t\x0f%\x0fA\x0f^\x0fz\x0f\x96\x0f\xb3\x0f\xcf\x0f\xec\x10\t\x10&\x10C\x10a\x10~\x10\x9b\x10\xb9\x10\xd7\x10\xf5\x11\x13\x111\x11O\x11m\x11\x8c\x11\xaa\x11\xc9\x11\xe8\x12\x07\x12&\x12E\x12d\x12\x84\x12\xa3\x12\xc3\x12\xe3\x13\x03\x13#\x13C\x13c\x13\x83\x13\xa4\x13\xc5\x13\xe5\x14\x06\x14\'\x14I\x14j\x14\x8b\x14\xad\x14\xce\x14\xf0\x15\x12\x154\x15V\x15x\x15\x9b\x15\xbd\x15\xe0\x16\x03\x16&\x16I\x16l\x16\x8f\x16\xb2\x16\xd6\x16\xfa\x17\x1d\x17A\x17e\x17\x89\x17\xae\x17\xd2\x17\xf7\x18\x1b\x18@\x18e\x18\x8a\x18\xaf\x18\xd5\x18\xfa\x19 \x19E\x19k\x19\x91\x19\xb7\x19\xdd\x1a\x04\x1a*\x1aQ\x1aw\x1a\x9e\x1a\xc5\x1a\xec\x1b\x14\x1b;\x1bc\x1b\x8a\x1b\xb2\x1b\xda\x1c\x02\x1c*\x1cR\x1c{\x1c\xa3\x1c\xcc\x1c\xf5\x1d\x1e\x1dG\x1dp\x1d\x99\x1d\xc3\x1d\xec\x1e\x16\x1e@\x1ej\x1e\x94\x1e\xbe\x1e\xe9\x1f\x13\x1f>\x1fi\x1f\x94\x1f\xbf\x1f\xea \x15 A l \x98 \xc4 \xf0!\x1c!H!u!\xa1!\xce!\xfb"\'"U"\x82"\xaf"\xdd#\n#8#f#\x94#\xc2#\xf0$\x1f$M$|$\xab$\xda%\t%8%h%\x97%\xc7%\xf7&\'&W&\x87&\xb7&\xe8\'\x18\'I\'z\'\xab\'\xdc(\r(?(q(\xa2(\xd4)\x06)8)k)\x9d)\xd0*\x02*5*h*\x9b*\xcf+\x02+6+i+\x9d+\xd1,\x05,9,n,\xa2,\xd7-\x0c-A-v-\xab-\xe1.\x16.L.\x82.\xb7.\xee/$/Z/\x91/\xc7/\xfe050l0\xa40\xdb1\x121J1\x821\xba1\xf22*2c2\x9b2\xd43\r3F3\x7f3\xb83\xf14+4e4\x9e4\xd85\x135M5\x875\xc25\xfd676r6\xae6\xe97$7`7\x9c7\xd78\x148P8\x8c8\xc89\x059B9\x7f9\xbc9\xf9:6:t:\xb2:\xef;-;k;\xaa;\xe8<\'<e<\xa4<\xe3="=a=\xa1=\xe0> >`>\xa0>\xe0?!?a?\xa2?\xe2@#@d@\xa6@\xe7A)AjA\xacA\xeeB0BrB\xb5B\xf7C:C}C\xc0D\x03DGD\x8aD\xceE\x12EUE\x9aE\xdeF"FgF\xabF\xf0G5G{G\xc0H\x05HKH\x91H\xd7I\x1dIcI\xa9I\xf0J7J}J\xc4K\x0cKSK\x9aK\xe2L*LrL\xbaM\x02MJM\x93M\xdcN%NnN\xb7O\x00OIO\x93O\xddP\'PqP\xbbQ\x06QPQ\x9bQ\xe6R1R|R\xc7S\x13S_S\xaaS\xf6TBT\x8fT\xdbU(UuU\xc2V\x0fV\\V\xa9V\xf7WDW\x92W\xe0X/X}X\xcbY\x1aYiY\xb8Z\x07ZVZ\xa6Z\xf5[E[\x95[\xe5\\5\\\x86\\\xd6]\']x]\xc9^\x1a^l^\xbd_\x0f_a_\xb3`\x05`W`\xaa`\xfcaOa\xa2a\xf5bIb\x9cb\xf0cCc\x97c\xebd@d\x94d\xe9e=e\x92e\xe7f=f\x92f\xe8g=g\x93g\xe9h?h\x96h\xeciCi\x9ai\xf1jHj\x9fj\xf7kOk\xa7k\xfflWl\xafm\x08m`m\xb9n\x12nkn\xc4o\x1eoxo\xd1p+p\x86p\xe0q:q\x95q\xf0rKr\xa6s\x01s]s\xb8t\x14tpt\xccu(u\x85u\xe1v>v\x9bv\xf8wVw\xb3x\x11xnx\xccy*y\x89y\xe7zFz\xa5{\x04{c{\xc2|!|\x81|\xe1}A}\xa1~\x01~b~\xc2\x7f#\x7f\x84\x7f\xe5\x80G\x80\xa8\x81\n\x81k\x81\xcd\x820\x82\x92\x82\xf4\x83W\x83\xba\x84\x1d\x84\x80\x84\xe3\x85G\x85\xab\x86\x0e\x86r\x86\xd7\x87;\x87\x9f\x88\x04\x88i\x88\xce\x893\x89\x99\x89\xfe\x8ad\x8a\xca\x8b0\x8b\x96\x8b\xfc\x8cc\x8c\xca\x8d1\x8d\x98\x8d\xff\x8ef\x8e\xce\x8f6\x8f\x9e\x90\x06\x90n\x90\xd6\x91?\x91\xa8\x92\x11\x92z\x92\xe3\x93M\x93\xb6\x94 \x94\x8a\x94\xf4\x95_\x95\xc9\x964\x96\x9f\x97\n\x97u\x97\xe0\x98L\x98\xb8\x99$\x99\x90\x99\xfc\x9ah\x9a\xd5\x9bB\x9b\xaf\x9c\x1c\x9c\x89\x9c\xf7\x9dd\x9d\xd2\x9e@\x9e\xae\x9f\x1d\x9f\x8b\x9f\xfa\xa0i\xa0\xd8\xa1G\xa1\xb6\xa2&\xa2\x96\xa3\x06\xa3v\xa3\xe6\xa4V\xa4\xc7\xa58\xa5\xa9\xa6\x1a\xa6\x8b\xa6\xfd\xa7n\xa7\xe0\xa8R\xa8\xc4\xa97\xa9\xa9\xaa\x1c\xaa\x8f\xab\x02\xabu\xab\xe9\xac\\\xac\xd0\xadD\xad\xb8\xae-\xae\xa1\xaf\x16\xaf\x8b\xb0\x00\xb0u\xb0\xea\xb1`\xb1\xd6\xb2K\xb2\xc2\xb38\xb3\xae\xb4%\xb4\x9c\xb5\x13\xb5\x8a\xb6\x01\xb6y\xb6\xf0\xb7h\xb7\xe0\xb8Y\xb8\xd1\xb9J\xb9\xc2\xba;\xba\xb5\xbb.\xbb\xa7\xbc!\xbc\x9b\xbd\x15\xbd\x8f\xbe\n\xbe\x84\xbe\xff\xbfz\xbf\xf5\xc0p\xc0\xec\xc1g\xc1\xe3\xc2_\xc2\xdb\xc3X\xc3\xd4\xc4Q\xc4\xce\xc5K\xc5\xc8\xc6F\xc6\xc3\xc7A\xc7\xbf\xc8=\xc8\xbc\xc9:\xc9\xb9\xca8\xca\xb7\xcb6\xcb\xb6\xcc5\xcc\xb5\xcd5\xcd\xb5\xce6\xce\xb6\xcf7\xcf\xb8\xd09\xd0\xba\xd1<\xd1\xbe\xd2?\xd2\xc1\xd3D\xd3\xc6\xd4I\xd4\xcb\xd5N\xd5\xd1\xd6U\xd6\xd8\xd7\\\xd7\xe0\xd8d\xd8\xe8\xd9l\xd9\xf1\xdav\xda\xfb\xdb\x80\xdc\x05\xdc\x8a\xdd\x10\xdd\x96\xde\x1c\xde\xa2\xdf)\xdf\xaf\xe06\xe0\xbd\xe1D\xe1\xcc\xe2S\xe2\xdb\xe3c\xe3\xeb\xe4s\xe4\xfc\xe5\x84\xe6\r\xe6\x96\xe7\x1f\xe7\xa9\xe82\xe8\xbc\xe9F\xe9\xd0\xea[\xea\xe5\xebp\xeb\xfb\xec\x86\xed\x11\xed\x9c\xee(\xee\xb4\xef@\xef\xcc\xf0X\xf0\xe5\xf1r\xf1\xff\xf2\x8c\xf3\x19\xf3\xa7\xf44\xf4\xc2\xf5P\xf5\xde\xf6m\xf6\xfb\xf7\x8a\xf8\x19\xf8\xa8\xf98\xf9\xc7\xfaW\xfa\xe7\xfbw\xfc\x07\xfc\x98\xfd)\xfd\xba\xfeK\xfe\xdc\xffm\xff\xff'