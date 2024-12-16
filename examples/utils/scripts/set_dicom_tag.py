"""create_new_uids.py:
Script to set value of specified DICOM tag in DICOM objects available in specified folder.
"""

import os
import argparse
import glob

import pydicom
from pydicom import DataElement


def set_dicom_tag(folder, dicom_tag, VR, value, dry_run=True):
    """Search folder (and subfolders) for DICOM files and set value of specified DICOM tag

    Parameters
    ----------
    folder : Folder to (recursively) search for DICOM objects
    dicom_tag : DICOM tag specifying which DICOM tag to set value for (format as "0x0020000D")
    VR : Value representation of DICOM tag to set, needed in case the DICOM tag is missing
    value : Value to set
    dry_run : Dry run, (True)/False
    """
    # find dcm files
    dcm_files = glob.glob(os.path.join(folder, "**", "*.dcm"), recursive=True)
    replaced_dcm_values = set()
    # loop over dcm files
    for dcm_file in dcm_files:
        dcm = pydicom.read_file(dcm_file)
        # if dicom tag exists in current dcm file
        if int(dicom_tag, 16) in dcm:
            # record replaced value and set new value
            replaced_dcm_values.add(dcm[dicom_tag].value)
            dcm[dicom_tag] = DataElement(int(dicom_tag, 16), VR, value)
        else:
            # add dicom tag with new value
            dcm.add_new(dicom_tag, VR, value)
        if not dry_run:
            # write dcm file to disk
            pydicom.dcmwrite(dcm_file, dcm, write_like_original=False)
    if dry_run:
        print("Values of DICOM tag", dicom_tag, "that will be replaced with", value)
        print(list(replaced_dcm_values))


def main(folder, dicom_tag, VR, value, dry_run):
    set_dicom_tag(folder, dicom_tag, VR, value, dry_run)


if __name__ == "__main__":
    # define input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", action="store", required=True, dest="folder", help="Folder to process"
    )
    parser.add_argument(
        "-dt",
        action="store",
        required=True,
        dest="dicom_tag",
        help="DICOM tag to set value for",
    )
    parser.add_argument(
        "-VR",
        action="store",
        required=True,
        dest="VR",
        help="Value range for DICOM tag to set value for",
    )
    parser.add_argument(
        "-v",
        action="store",
        required=True,
        dest="value",
        help="Value to set DICOM tag to",
    )
    parser.add_argument("-dr", action="store_true", dest="dry_run", help="Dry run")
    parser.add_argument("-ndr", action="store_false", dest="dry_run", help="No dry run")
    parser.set_defaults(dry_run=True)

    # parse input arguments
    opts = parser.parse_args()

    # call main function
    main(opts.folder, opts.dicom_tag, opts.VR, opts.value, opts.dry_run)
