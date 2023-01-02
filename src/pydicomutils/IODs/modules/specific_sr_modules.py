from .general_modules import Module

class SRDocumentSeriesModule(Module):
    """SR Document Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Modality",
                                          "SeriesInstanceUID",
                                          "SeriesNumber",
                                          "ReferencedPerformedProcedureStepSequence"]
        self.optional_dicom_attributes = ["SeriesDate",
                                          "SeriesTime",
                                          "SeriesDescription"]

class SRDocumentGeneralModule(Module):
    """SR Document General Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["InstanceNumber",
                                          "CompletionFlag",
                                          "VerificationFlag",
                                          "ContentDate",
                                          "ContentTime",
                                          "PerformedProcedureCodeSequence",
                                          "CurrentRequestedProcedureEvidenceSequence"]
        self.optional_dicom_attributes = ["PreliminaryFlag"]

class SRDocumentContentModule(Module):
    """SR Document Content Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["ValueType",
                                          "ConceptNameCodeSequence",
                                          "ContinuityOfContent",
                                          "ContentSequence"]

class KeyObjectDocumentSeriesModule(Module):
    """Key Object Document Series Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["Modality",
                                          "SeriesInstanceUID",
                                          "SeriesNumber",
                                          "ReferencedPerformedProcedureStepSequence"]
        self.optional_dicom_attributes = ["SeriesDate",
                                          "SeriesTime",
                                          "SeriesDescription"]

class KeyObjectDocumentModule(Module):
    """Key Object Document Module class
    """
    def __init__(self):
        super().__init__()
        self.required_dicom_attributes = ["InstanceNumber",
                                          "ContentDate",
                                          "ContentTime",
                                          "CurrentRequestedProcedureEvidenceSequence"]
