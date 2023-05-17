"""create_new_uids.py:
Script to create new UIDs for specified DICOM tag in DICOM objects available
in specified folder.
"""
import os
import glob
import argparse

import pydicom
from pydicom import DataElement


def create_new_uids(folder, dicom_tag, dry_run=True):
    """Search folder (and subfolders) for DICOM files and create new UIDs for specified DICOM tag

    Parameters
    ----------
    folder : Folder to (recursively) search for DICOM objects
    dicom_tag : DICOM tag specifying which UID to create new UIDs for (format as "0x0020000D")
    dry_run : Dry run, (True)/False
    """
    # find dcm files
    dcm_files = glob.glob(os.path.join(folder, "**", "*.dcm"), recursive=True)
    dcm_dict = dict()
    # loop over dcm files
    for dcm_file in dcm_files:
        dcm = pydicom.read_file(dcm_file)
        # if dicom tag exists in current dcm file
        if int(dicom_tag, 16) in dcm:
            # record replaceed uid and set new uid
            uid = dcm[dicom_tag].value
            if uid not in dcm_dict:
                dcm_dict[uid] = pydicom.uid.generate_uid()
            dcm[dicom_tag] = DataElement(int(dicom_tag, 16), "UI", dcm_dict[uid])
        else:
            # add dicom tag with new uid
            uid = pydicom.uid.generate_uid()
            dcm[dicom_tag] = DataElement(int(dicom_tag, 16), "UI", uid)
        if not dry_run:
            # write dcm file to disk
            pydicom.write_file(dcm_file, dcm, write_like_original=False)
    if dry_run:
        print("Uids to update")
        print(dcm_file)


def main(folder, dicom_tag, dry_run):
    create_new_uids(folder, dicom_tag, dry_run)


if __name__ == "__main__":
    # define input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", action="store", required=True, dest="folder", help="Folder to process"
    )
    parser.add_argument(
        "-d",
        action="store",
        required=True,
        dest="dicom_tag",
        help="DICOM tag to create new uids for",
    )
    parser.add_argument("-dr", action="store_true", dest="dry_run", help="Dry run")
    parser.add_argument("-ndr", action="store_false", dest="dry_run", help="No dry run")
    parser.set_defaults(dry_run=True)

    # parse input arguments
    opts = parser.parse_args()

    # call main function
    main(opts.folder, opts.dicom_tag, opts.dry_run)
