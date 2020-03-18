import os
import glob
import pydicom
import numpy as np

def read_and_sort_dicom_files(dcm_files, return_dcm_files = False):
    # list, read, sort template dicom files
    dcm_handlers = [pydicom.read_file(item, force=True) for item in dcm_files]

    # sort in ascending order
    z_positions = []
    for dcm_handler in dcm_handlers:
        x = dcm_handler.ImageOrientationPatient[0:3]
        y = dcm_handler.ImageOrientationPatient[3:6]
        z_dir = np.cross(x,y)
        z_positions.append(np.dot(z_dir, dcm_handler.ImagePositionPatient))
    sorted_dcm_handlers = [x for (y,x) in sorted(zip(z_positions, dcm_handlers))]
    sorted_dcm_files = [x for (y,x) in sorted(zip(z_positions, dcm_files))]

    if return_dcm_files:
        return sorted_dcm_files
    else:
        return sorted_dcm_handlers

def construct_T_R_S_from_dcm_handlers(dcm_handlers):
    # extract information needed for patient to raw transform
    x_dir = dcm_handlers[0].ImageOrientationPatient[0:3]
    x_dir = x_dir / np.linalg.norm(x_dir)
    y_dir = dcm_handlers[0].ImageOrientationPatient[3:6]
    y_dir = y_dir / np.linalg.norm(y_dir)
    z_dir = np.array(dcm_handlers[1].ImagePositionPatient) - np.array(dcm_handlers[0].ImagePositionPatient)
    x_spacing = np.array(dcm_handlers[0].PixelSpacing[0])
    y_spacing = np.array(dcm_handlers[0].PixelSpacing[1])
    z_spacing = np.linalg.norm(z_dir)
    z_dir = z_dir / np.linalg.norm(z_dir)

    # create patient to raw transform
    r = np.concatenate((np.expand_dims(x_dir,1),
                        np.expand_dims(y_dir,1),
                        np.expand_dims(z_dir,1)),axis=1)
    s = np.diag([x_spacing, y_spacing, z_spacing])
    t = np.expand_dims(np.array(dcm_handlers[0].ImagePositionPatient),1)
    R = np.diag([1.0, 1.0, 1.0, 1.0])
    R[0:3,0:3] = r
    S = np.diag([1.0, 1.0, 1.0, 1.0])
    S[0:3,0:3] = s
    T = np.diag([1.0, 1.0, 1.0, 1.0])
    T[3,3] = 1.0
    T[0:3,3] = t[:,0]

    return T, R, S