import os
import shutil
import glob
import logging

from pydicom import read_file

from pydicomutils.IODs.GSPS import GSPS
from pydicomutils.IODs.KOS import KOS

from utils.misc.color import WHITE, PURPLE, ORANGE, BLUE
from utils.misc.dcm_io_helper import read_and_sort_dicom_files

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("pydicomutils_examples.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def run():
    logger.info("Starting")
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Set output folder
    output_folder = os.path.join(output_folder, "data", "ct_images", "gsps_and_kos")
    os.makedirs(output_folder, exist_ok=True)

    # Find original images
    input_folder = os.path.join(
        file_folder, "data", "ct_images", "original_dicom_images"
    )
    dcm_files = glob.glob(os.path.join(input_folder, "*.dcm"))
    sorted_dcm_files = read_and_sort_dicom_files(dcm_files, return_dcm_files=True)

    # Copy original images to output folder
    ds = read_file(dcm_files[0])
    dcm_folder = os.path.join(output_folder, "series_" + str(ds.SeriesNumber))
    os.makedirs(dcm_folder, exist_ok=True)
    for dcm_file in dcm_files:
        shutil.copy(dcm_file, dcm_folder)

    # Create GSPS objects
    logger.info("GSPS")
    gsps = GSPS()
    gsps.create_empty_iod()
    gsps.initiate(sorted_dcm_files)
    gsps.set_dicom_attribute("SeriesNumber", "500")
    gsps.set_dicom_attribute("SeriesDescription", "Annotation examples")
    gsps.set_dicom_attribute("ContentLabel", "GSPSANNOTATIONS")
    gsps.set_dicom_attribute("RescaleIntercept", "-1024.0")
    gsps.set_dicom_attribute("RescaleSlope", "1.0")
    gsps.set_dicom_attribute("RescaleType", "HU")
    gsps.set_dicom_attribute(
        "SoftcopyVOILUTSequence", [{"WindowCenter": "-600", "WindowWidth": "1500"}]
    )
    gsps.add_graphical_layer("LAYER1", 1, recommended_cielab_value=WHITE.dcm_format())
    gsps.add_graphical_layer("LAYER2", 2, recommended_cielab_value=BLUE.dcm_format())
    gsps.add_graphical_layer(
        "SCROLLBAR", 3, recommended_cielab_value=WHITE.dcm_format()
    )
    gsps.add_graphic_object(
        dcm_files[0], "LAYER1", [50, 50, 50, 100, 100, 100, 100, 50, 50, 50], "POLYLINE"
    )
    gsps.add_graphic_object(dcm_files[0], "LAYER1", [256, 256], "POINT")
    gsps.add_graphic_object(
        dcm_files[0],
        "LAYER1",
        [200, 200, 300, 300, 400, 400, 500, 500],
        "POLYLINE",
        cielab_value=PURPLE.dcm_format(),
        shadow_style="NORMAL",
        line_thickness=5.0,
    )
    gsps.add_graphic_object(
        dcm_files[0],
        "LAYER2",
        [70, 70, 70, 170, 170, 170, 120, 120, 170, 70, 70, 70],
        "POLYLINE",
        graphic_filled="Y",
    )
    gsps.add_graphic_object(dcm_files[0], "LAYER2", [200, 200, 300, 300], "CIRCLE")
    gsps.add_text_object(dcm_files[0], "LAYER1", "Text in layer 1", [25.0, 25.0])
    gsps.add_text_object(dcm_files[0], "LAYER2", "Text in layer 2", [170.0, 170.0])

    ind_finding = 0
    for item in sorted_dcm_files:
        item_ds = read_file(item)
        if item_ds.SOPInstanceUID == ds.SOPInstanceUID:
            break
        ind_finding += 1
    for ind, dcm_file in enumerate(sorted_dcm_files):
        gsps.add_graphic_object(
            dcm_file,
            "SCROLLBAR",
            [505, 50, 507, 50, 507, 461, 505, 461, 505, 50],
            "POLYLINE",
        )
        gsps.add_graphic_object(
            dcm_file,
            "SCROLLBAR",
            [
                497,
                int(
                    50
                    + (461.0 - 50.0)
                    / float(len(dcm_files) - 1)
                    * (len(dcm_files) - ind_finding - 1)
                ),
                501,
                int(
                    50
                    + (461.0 - 50.0)
                    / float(len(dcm_files) - 1)
                    * (len(dcm_files) - ind_finding - 1)
                ),
            ],
            "POLYLINE",
            cielab_value=ORANGE.dcm_format(),
            line_thickness=3.0,
            shadow_style="OFF",
        )
        gsps.add_graphic_object(
            dcm_file,
            "SCROLLBAR",
            [
                503,
                int(
                    50
                    + (461.0 - 50.0)
                    / float(len(sorted_dcm_files) - 1)
                    * (len(sorted_dcm_files) - ind - 1)
                ),
                509,
                int(
                    50
                    + (461.0 - 50.0)
                    / float(len(sorted_dcm_files) - 1)
                    * (len(sorted_dcm_files) - ind - 1)
                ),
            ],
            "POLYLINE",
        )
    os.makedirs(
        os.path.join(
            output_folder, "series_" + str(gsps.dataset.SeriesNumber).zfill(3)
        ),
        exist_ok=True,
    )
    output_file = os.path.join(
        output_folder, "series_" + str(gsps.dataset.SeriesNumber).zfill(3), "pr.dcm"
    )
    gsps.write_to_file(output_file, write_like_original=False)

    # Create KOS objects
    logger.info("KOS")
    kos = KOS()
    kos.create_empty_iod()
    kos.initiate(dcm_files)
    kos.set_dicom_attribute("SeriesNumber", "600")
    kos.set_dicom_attribute("SeriesDescription", "Key Object Selection")
    kos.add_key_documents([dcm_files[0]])
    os.makedirs(
        os.path.join(output_folder, "series_" + str(kos.dataset.SeriesNumber).zfill(3)),
        exist_ok=True,
    )
    output_file = os.path.join(
        output_folder, "series_" + str(kos.dataset.SeriesNumber).zfill(3), "kos.dcm"
    )
    kos.write_to_file(output_file, write_like_original=False)


if __name__ == "__main__":
    run()
