from .general_modules import Module

class PresentationSeriesModule(Module):
    """Presentation Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Modality"]
        
class PresentationStateIdentificationModule(Module):
    """Presentation State Identification Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PresentationCreationDate",
                                          "PresentationCreationTime",
                                          "InstanceNumber",
                                          "ContentLabel",
                                          "ContentDescription",
                                          "ContentCreatorName"]

class PresentationStateRelationshipModule(Module):
    """Presentation State Relationship Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ReferencedSeriesSequence"]

class DisplayedAreaModule(Module):
    """Displayed Area Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["DisplayedAreaSelectionSequence"]

class GraphicAnnotationModule(Module):
    """Graphic Annotation Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["GraphicAnnotationSequence"]

class GraphicLayerModule(Module):
    """Graphic Layer Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["GraphicLayerSequence"]

class SoftcopyPresentationLUTModule(Module):
    """Softcopy Presenation LUT Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["PresentationLUTShape"]