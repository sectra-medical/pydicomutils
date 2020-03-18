from .general_modules import Module

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