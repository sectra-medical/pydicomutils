from pydicom import Dataset

from .IOD import IOD, IODTypes
from .modules.specific_image_modules import CRSeriesModule, CRImageModule

class CRImage(IOD):
    """Implementation of the CR Image IOD
    ----------
    """
    def __init__(self):
        super().__init__(IODTypes.CRImage)

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
            cr_specific_image_modules = [CRSeriesModule(),
                                         CRImageModule()]
            for module in cr_specific_image_modules:
                module.copy_required_dicom_attributes(dataset_to_copy_from, 
                                                    self.dataset)
                if include_optional:
                    module.copy_optional_dicom_attributes(dataset_to_copy_from, 
                                                        self.dataset)
    
    def initiate(self):
        """Initiate the IOD by setting some dummy values for required attributes
        """
        super().initiate()

        # CR image module
        self.dataset.PhotometricInterpretation = "MONOCHROME2"
        self.dataset.PixelSpacing = [str(1.0), str(1.0)]

    def add_pixel_data(self, pixel_array,
                       photometric_interpretation="MONOCHROME2",
                       pixel_spacing=None):
        """Add pixel data
        
        Arguments:
            pixel_array {2D np.array} -- The pixel data to add to the CR object
        
        Keyword Arguments:
            photometric_interpretation {str} -- Photometric interpretation of the provided pixel_array (default: {"MONOCHROME2"})
            pixel_spacing {[str str]} -- Pixel spacing of the provided pixel_array (default: {None})
        """
        if pixel_spacing is None:
            pixel_spacing = [str(1.0), str(1.0)]
        if len(pixel_array.shape) != 2:
            print("Unsupported number of samples per pixel",pixel_array.shape[2],
                  "only samples per pixel is supported")
        else:
            self.dataset.SamplesPerPixel = 1
        self.dataset.PhotometricInterpretation = photometric_interpretation
        self.dataset.Rows = pixel_array.shape[1]
        self.dataset.Columns = pixel_array.shape[0]
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
        self.dataset.PixelSpacing = pixel_spacing
        self.dataset.PixelData = pixel_array.tobytes()