import os
import shutil
import glob
from pydicom import read_file
from pydicomutils.misc.dcm_io_helper import read_and_sort_dicom_files
from pydicomutils.scripts.convert_seg_to_gsps import convert_seg_to_gsps

if __name__ == "__main__":
    file_folder = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(file_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # set output folder
    output_folder = os.path.join(output_folder, "data", "ct_images", "gsps_from_seg")
    os.makedirs(output_folder, exist_ok=True)

    # find original images
    input_folder = os.path.join(file_folder, "data", "ct_images", "original_dicom_images")
    dcm_files = glob.glob(os.path.join(input_folder,"*.dcm"))
    sorted_dcm_files = read_and_sort_dicom_files(dcm_files, return_dcm_files=True)
    
    # copy original images to output folder
    ds = read_file(dcm_files[0])
    dcm_folder = os.path.join(output_folder, "series_" + str(ds.SeriesNumber))
    os.makedirs(dcm_folder, exist_ok=True)
    for dcm_file in dcm_files:
        shutil.copy(dcm_file, dcm_folder)

    # run conversion of seg to gsps
    input_file = glob.glob(os.path.join(file_folder, "data", "ct_images", "dcm_segmentation","*.dcm"))[0]
    convert_seg_to_gsps(input_file, output_folder)