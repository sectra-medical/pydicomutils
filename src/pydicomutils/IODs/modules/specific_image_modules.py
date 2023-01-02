from .general_modules import Module

class SCEquipmentModule(Module):
    """SC Equipment Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ConversionType"]

class CRSeriesModule(Module):
    """CR Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["BodyPartExamined",
                                          "ViewPosition"]

class CRImageModule(Module):
    """CR Image Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PhotometricInterpretation",
                                          "PixelSpacing"]

class CTImageModule(Module):
    """CT Image Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ImageType",
                                          "SamplesPerPixel",
                                          "PhotometricInterpretation",
                                          "BitsAllocated",
                                          "BitsStored",
                                          "HighBit",
                                          "RescaleIntercept",
                                          "RescaleSlope",
                                          "RescaleType",
                                          "KVP",
                                          "AcquisitionNumber"]

class SCImageModule(Module):
    """SC Image Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PixelSpacing"]

class WholeSlideMicroscopySeriesModule(Module):
    """Whole Slide Microscopy Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = []

class WholeSlideMicroscopyImageModule(Module):
    """Whole Slide Microscopy Image Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ImageType",
                                          "ImagedVolumeWidth",
                                          "ImagedVolumeHeight",
                                          "ImagedVolumeDepth",
                                          "TotalPixelMatrixColumns",
                                          "TotalPixelMatrixRows",
                                          "TotalPixelMatrixOriginSequence",
                                          "ImageOrientationSlide",
                                          "SamplesPerPixel",
                                          "PhotometricInterpretation",
                                          "NumberOfFrames",
                                          "BitsAllocated",
                                          "BitsStored",
                                          "HighBit",
                                          "AcquisitionDateTime",
                                          "AcquisitionDuration",
                                          "LossyImageCompression",
                                          "VolumetricProperties",
                                          "SpecimenLabelInImage",
                                          "BurnedInAnnotation",
                                          "FocusMethod",
                                          "ExtendedDepthOfField"]

class OpticalPathModule(Module):
    """Optical Path Module Class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["OpticalPathSequence"]