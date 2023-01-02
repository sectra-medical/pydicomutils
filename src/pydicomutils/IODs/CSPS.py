from datetime import datetime

from pydicom import Dataset, read_file

from .IOD import IOD, IODTypes, SOP_CLASS_UID_MODALITY_DICT
from .modules.specific_presentation_state_modules import PresentationSeriesModule
from .modules.specific_presentation_state_modules import PresentationStateIdentificationModule
from .modules.specific_presentation_state_modules import PresentationStateRelationshipModule
from .modules.specific_presentation_state_modules import DisplayedAreaModule
from .sequences.Sequences import generate_sequence, generate_RS_sequence, generate_DAS_sequence

class CSPS(IOD):
    """Implementation of the Color Softcopy Presentation State IOD
    """
    def __init__(self):
        super().__init__(IODTypes.CSPS)

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
            pr_specific_modules = [PresentationModule(),
                                   PresentationStateIdentificationModule(),
                                   PresentationStateRelationshipModule(),
                                   DisplayedAreaModule()]
            for module in pr_specific_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                      self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                          self.dataset)
        
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
        # presentation series module
        self.dataset.Modality = SOP_CLASS_UID_MODALITY_DICT[self.iod_type]
        # presentation state identification module
        self.dataset.PresentationCreationDate = datetime.now().strftime("%Y%m%d")
        self.dataset.PresentationCreationTime = datetime.now().strftime("%H%M%S")
        self.dataset.InstanceNumber = str(1)
        self.dataset.ContentLabel = "PRESENTATION_STATE"
        # presentation state relationship module
        if referenced_dcm_files:
            self.dataset.ReferencedSeriesSequence = generate_RS_sequence(referenced_dcm_files)
        # displayed area module
        if referenced_dcm_files:
            self.dataset.DisplayedAreaSelectionSequence = generate_DAS_sequence(referenced_dcm_files)
        # soft copy presentation LUT module
        self.dataset.PresentationLUTShape = "IDENTITY"

    def add_graphical_layer(self, layer_name, layer_order,
                            recommended_grayscale_value = None,
                            recommended_cielab_value = None,
                            layer_description = None):
        """Add graphical layer
        
        Arguments:
            layer_name {str} -- Name of layer
            layer_order {int} -- Order of layer
        
        Keyword Arguments:
            recommended_grayscale_value {[type]} -- [description] (default: {None})
            recommended_cielab_value {[type]} -- [description] (default: {None})
            layer_description {[type]} -- [description] (default: {None})
        """
        ds = Dataset()
        ds.GraphicLayer = layer_name
        ds.GraphicLayerOrder = layer_order
        if recommended_grayscale_value is not None:
            ds.GraphicLayerRecommendedDisplayGrayscaleValue = recommended_grayscale_value
        if recommended_cielab_value is not None:
            ds.GraphicLayerRecommendedDisplayCIELabValue = recommended_cielab_value
        if layer_description is not None:
            ds.GraphicLayerDescription = layer_description
        if "GraphicLayerSequence" not in self.dataset:
            self.dataset.GraphicLayerSequence = generate_sequence("GraphicLayerSequence", [{}])
        self.dataset.GraphicLayerSequence.append(ds)

    def add_graphic_object(self, referenced_dcm_file, layer_name,
                           graphic_data, graphic_type, 
                           graphic_filled = None,
                           cielab_value = None, 
                           shadow_style = None,
                           line_thickness = None):
        """Add graphical object
        
        Arguments:
            referenced_dcm_file {[type]} -- [description]
            layer_name {[type]} -- [description]
            graphic_data {[type]} -- [description]
            graphic_type {[type]} -- [description]
        
        Keyword Arguments:
            graphic_filled {[type]} -- [description] (default: {None})
            cielab_value {[type]} -- [description] (default: {None})
            shadow_style {[type]} -- [description] (default: {None})
            line_thickness {[type]} -- [description] (default: {None})
        """
        ds = Dataset()
        ds_ref = read_file(referenced_dcm_file)
        ds.ReferencedImageSequence = generate_sequence("ReferencedImageSequence", 
                                                       [{
                                                           "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                                           "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID
                                                       }])
        ds.GraphicLayer = layer_name
        ds.GraphicObjectSequence = generate_sequence("GraphicObjectSequence", 
                                                     [{
                                                         "GraphicAnnotationUnits": "PIXEL",
                                                         "GraphicDimensions": 2,
                                                         "NumberOfGraphicPoints": int(len(graphic_data) / 2),
                                                         "GraphicData": graphic_data,
                                                         "GraphicType": graphic_type,
                                                     }])
        if graphic_filled:
            ds.GraphicObjectSequence[0].GraphicFilled = graphic_filled
        if cielab_value or shadow_style or line_thickness:
            ds.GraphicObjectSequence[0].LineStyleSequence = generate_sequence("LineStyleSequence", [{}])
            if cielab_value:
                ds.GraphicObjectSequence[0].LineStyleSequence[0].PatternOnColorCIELabValue = cielab_value
            if shadow_style:
                ds.GraphicObjectSequence[0].LineStyleSequence[0].ShadowStyle = shadow_style
            if line_thickness:
                ds.GraphicObjectSequence[0].LineStyleSequence[0].LineThickness = line_thickness
        if graphic_filled and cielab_value:
            ds.GraphicObjectSequence[0].FillStyleSequence = generate_sequence("FillStyleSequence", [{}])
            if cielab_value:
                ds.GraphicObjectSequence[0].FillStyleSequence[0].PatternOnColorCIELabValue = cielab_value
        if "GraphicAnnotationSequence" not in self.dataset:
            self.dataset.GraphicAnnotationSequence = generate_sequence("GraphicAnnotationSequence", [{}])
        self.dataset.GraphicAnnotationSequence.append(ds)
    
    def add_text_object(self, referenced_dcm_file, layer_name,
                        text_value, anchor_point, 
                        cielab_value = None, 
                        shadow_style = None):
        """Add text object
        
        Arguments:
            referenced_dcm_file {[type]} -- [description]
            layer_name {[type]} -- [description]
            text_value {[type]} -- [description]
            anchor_point {[type]} -- [description]
        
        Keyword Arguments:
            cielab_value {[type]} -- [description] (default: {None})
            shadow_style {[type]} -- [description] (default: {None})
        """
        ds = Dataset()
        ds_ref = read_file(referenced_dcm_file)
        ds.ReferencedImageSequence = generate_sequence("ReferencedImageSequence", 
                                                       [{
                                                           "ReferencedSOPClassUID": ds_ref.SOPClassUID,
                                                           "ReferencedSOPInstanceUID": ds_ref.SOPInstanceUID
                                                       }])
        ds.GraphicLayer = layer_name
        ds.TextObjectSequence = generate_sequence("TextObjectSequence", 
                                                  [{
                                                      "AnchorPointAnnotationUnits": "PIXEL",
                                                      "UnformattedTextValue": text_value,
                                                      "AnchorPoint": anchor_point,
                                                      "AnchorPointVisibility": "N",
                                                  }])
        if cielab_value or shadow_style:
            ds.TextObjectSequence[0].TextStyleSequence = generate_sequence("TextStyleSequence", [{}])
            if cielab_value:
                ds.TextObjectSequence[0].TextStyleSequence[0].TextColorCIELabValue = cielab_value
            if shadow_style:
                ds.TextObjectSequence[0].TextStyleSequence[0].ShadowStyle = shadow_style
        if "GraphicAnnotationSequence" not in self.dataset:
            self.dataset.GraphicAnnotationSequence = generate_sequence("GraphicAnnotationSequence", [{}])
        self.dataset.GraphicAnnotationSequence.append(ds)