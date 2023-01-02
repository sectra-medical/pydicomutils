from pydicom import Dataset

from .IOD import IOD, IODTypes
from .modules.specific_image_modules import SCEquipmentModule, SCImageModule

class SCImage(IOD):
    """Implementation of the SC Image IOD
    ----------
    """
    def __init__(self):
        super().__init__(IODTypes.SCImage)

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
            sc_specific_image_modules = [SCEquipmentModule(),
                                         SCImageModule()]
            for module in sc_specific_image_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                    self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                        self.dataset)
    
    def initiate(self):
        """Initiate the IOD by setting some dummy values for required attributes
        """
        super().initiate()

        # SC Equipment
        self.dataset.ConversionType = "SYN"
        # SC image module
        self.dataset.PixelSpacing = [str(1.0), str(1.0)]

    def add_pixel_data(self, pixel_array,
                       photometric_interpretation="MONOCHROME2",
                       pixel_spacing=None):
        """Add pixel data
        
        Arguments:
            pixel_array {2/3D np.array} -- The pixel data to add to the SC object
        
        Keyword Arguments:
            photometric_interpretation {str} -- Photometric interpretation of the provided pixel_array (default: {"MONOCHROME2"})
            pixel_spacing {[str str]} -- Pixel spacing of the provided pixel_array (default: {["1.0", "1.0"]})
        """
        if pixel_spacing is None:
            pixel_spacing = [str(1.0), str(1.0)]
        if len(pixel_array.shape) == 2:
            self.dataset.SamplesPerPixel = 1
        elif len(pixel_array.shape) == 3 and pixel_array.shape[2] == 3:
            self.dataset.SamplesPerPixel = 3
        else:
            print(f"Unsupported number of samples per pixel {pixel_array.shape[2]}, as only 1 or 3 samples per pixel is supported")
            return
        self.dataset.PhotometricInterpretation = photometric_interpretation
        if self.dataset.SamplesPerPixel == 3 and photometric_interpretation != "RGB":
            self.dataset.PhotometricInterpretation = "RGB"
            print(f"Unsupported photometric intpretation, forcing RGB")
        if self.dataset.SamplesPerPixel == 3:
            self.dataset.PlanarConfiguration = 0
        self.dataset.Rows = pixel_array.shape[0]
        self.dataset.Columns = pixel_array.shape[1]
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
            print(f"Unsupported pixel type {pixel_array.dtype}, as only uint8 and uint16 is supported")
        self.dataset.PixelSpacing = pixel_spacing
        self.dataset.PixelData = pixel_array.tobytes()