import os
import numpy as np
from datetime import datetime
from skimage import measure
from pydicom import read_file
from pydicomutils.IODs.GSPS import GSPS

def parse_and_construct_graphic_layer(ds):
    """Parse DICOM Dataset and construct json representation of GraphicLayerSequence

    Parameters
    ----------
    ds : DICOM Dataset
    """
    graphic_layers = list()
    for item in ds.SegmentSequence:
        layer = {
            "GraphicLayer": str(item.SegmentDescription).upper(),
            "GraphicLayerOrder": item.SegmentNumber,
            "GraphicLayerRecommendedDisplayCIELabValue": [49512, 38656, 52736]
        }
        graphic_layers.append(layer)
    return graphic_layers

def parse_and_construct_referenced_series_seqeuence(ds):
    """Parse DICOM Dataset and construct json representation of ReferencedSeriesSequence

    Parameters
    ----------
    ds : DICOM Dataset
    """
    referenced_series_seqeuence = list()
    for referenced_series in ds.ReferencedSeriesSequence:
        referenced_instance_seqeuence = list()
        for referenced_instance in referenced_series.ReferencedInstanceSequence:
            instance = {
                "ReferencedSOPClassUID": referenced_instance.ReferencedSOPClassUID,
                "ReferencedSOPInstanceUID": referenced_instance.ReferencedSOPInstanceUID
            }
            referenced_instance_seqeuence.append(instance)
        series = {
            "ReferencedImageSequence": referenced_instance_seqeuence,
            "SeriesInstanceUID": referenced_series.SeriesInstanceUID
        }
        referenced_series_seqeuence.append(series)
    return referenced_series_seqeuence

def parse_and_construct_referenced_image_sequence(ds):
    """Parse DICOM Dataset and construct json representation of ReferencedImageSequence

    Parameters
    ----------
    ds : DICOM Dataset
    """
    referenced_series_seqeuence = list()
    for referenced_series in ds.ReferencedSeriesSequence:
        referenced_instance_seqeuence = list()
        for referenced_instance in referenced_series.ReferencedInstanceSequence:
            instance = {
                "ReferencedSOPClassUID": referenced_instance.ReferencedSOPClassUID,
                "ReferencedSOPInstanceUID": referenced_instance.ReferencedSOPInstanceUID
            }
            referenced_instance_seqeuence.append(instance)
        series = {
            "ReferencedImageSequence": referenced_instance_seqeuence
        }
        referenced_series_seqeuence.append(series)
    return referenced_series_seqeuence

def parse_and_construct_graphic_annotation_sequence(ds):
    """Parse DICOM Dataset and construct json representation of GraphicAnnotationSequence

    Parameters
    ----------
    ds : DICOM Dataset
    """
    # Initiate output
    graphic_annotation_sequence = list()
    # Get segmentation data and flip axes
    pixel_array = ds.pixel_array
    segmentation_volume = np.transpose(pixel_array, (2, 1, 0))
    frame_no = 0
    # For each frame
    for frame in ds.PerFrameFunctionalGroupsSequence:
        # Get segmentation map
        segmentation_map = segmentation_volume[:,:,frame_no]
        frame_no += 1
        # Extract contours
        contours = measure.find_contours(segmentation_map, 0.5)
        if len(contours) < 1:
            continue
        graphic_object_sequence = list()
        # For each contour
        for contour in contours:
            # Create graphic object
            graphic_object = {
                "GraphicAnnotationUnits": "PIXEL",
                "GraphicDimensions": 2,
                "NumberOfGraphicPoints": len(contour),
                "GraphicData": contour.ravel().tolist(),
                "GraphicType": "POLYLINE" 
            }
            graphic_object_sequence.append(graphic_object)
        # Create graphic annotation
        graphic_annotation = {
            "ReferencedImageSequence": [{
                "ReferencedSOPClassUID": frame.DerivationImageSequence[0].SourceImageSequence[0].ReferencedSOPClassUID,
                "ReferencedSOPInstanceUID": frame.DerivationImageSequence[0].SourceImageSequence[0].ReferencedSOPInstanceUID,
            }],
            "GraphicLayer": str(ds.SegmentSequence[frame.SegmentIdentificationSequence[0].ReferencedSegmentNumber - 1].SegmentDescription).upper(),
            "GraphicObjectSequence": graphic_object_sequence
        }
        graphic_annotation_sequence.append(graphic_annotation)
    return graphic_annotation_sequence

def convert_seg_to_gsps(dcm_file, output_folder):
    """Convert DICOM SEG object to a DICOM GSPS object with polyline to
    indicate the contours of the segmentation maps
    
    Parameters
    ----------
    dcm_file : Original DICOM SEG object
    output_folder : Study folder to place DICOM GSPS object in
    """
    # Read DICOM file
    ds = read_file(dcm_file)
    # Parse and create necessary data
    graphic_layer = parse_and_construct_graphic_layer(ds)
    referenced_series_sequence = parse_and_construct_referenced_series_seqeuence(ds)
    referenced_image_sequence = parse_and_construct_referenced_image_sequence(ds)
    graphic_annotation_sequence = parse_and_construct_graphic_annotation_sequence(ds)

    gsps = GSPS()
    gsps.create_empty_iod()
    gsps.initiate([dcm_file])
    gsps.set_dicom_attribute("SeriesNumber", "500")
    gsps.set_dicom_attribute("SeriesDescription", "Contours from segmentation object")
    gsps.set_dicom_attribute("SeriesDate", datetime.now().strftime("%Y%m%d"))
    gsps.set_dicom_attribute("SeriesTime", datetime.now().strftime("%H%M%S"))
    gsps.set_dicom_attribute("ContentLabel", "SEGMENTATIONS")
    gsps.set_dicom_attribute("ReferencedSeriesSequence", referenced_series_sequence)
    gsps.set_dicom_attribute("DisplayedAreaSelectionSequence", [{
        "ReferencedImageSequence": referenced_image_sequence[0]["ReferencedImageSequence"],
        "DisplayedAreaTopLeftHandCorner": [1, 1],
        "DisplayedAreaBottomRightHandCorner": [int(ds.Columns), int(ds.Rows)],
        "PresentationSizeMode": "SCALE TO FIT",
        "PresentationPixelSpacing" : ds.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing
    }])
    gsps.set_dicom_attribute("GraphicAnnotationSequence", graphic_annotation_sequence)
    gsps.set_dicom_attribute("GraphicLayerSequence", graphic_layer)

    os.makedirs(os.path.join(output_folder,
                             "series_" + str(gsps.dataset.SeriesNumber).zfill(3)), 
                             exist_ok=True)
    output_file = os.path.join(output_folder,
                               "series_" + str(gsps.dataset.SeriesNumber).zfill(3), 
                               "pr.dcm")
    gsps.write_to_file(output_file, write_like_original=False)