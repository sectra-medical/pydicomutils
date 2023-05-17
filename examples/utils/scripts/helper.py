"""helper.py:
Script with some helper functions.
"""
import os
import glob
import platform
import shutil
import subprocess


def is_linux():
    """
    True if current system is Linux-based
    """
    return platform.system() == "Linux"


def mkdir(folder):
    """
    Specialized mkdir function using mkdir and chmod commands on Linux

    Parameters
    ----------
    """
    if is_linux():
        subprocess.run(["sudo", "mkdir", "-p", folder])
        subprocess.run(["sudo", "chmod", "777", folder])
    else:
        os.makedirs(folder, exist_ok=True)


def create_folder(folder, clear_folder=False):
    """
    Create specified folder and clear its content if already existent

    Parameters
    ----------
    """
    if not os.path.exists(folder):
        print("Creating folder:", folder)
        mkdir(folder)
    else:
        if len(glob.glob(os.path.join(folder, "*"))) > 0:
            print("Specified output folder alreay contains data.")
            if clear_folder:
                print("Will clear the folder before proceeding.")
                shutil.rmtree(folder, ignore_errors=True)
                if not os.path.exists(folder):
                    mkdir(folder)
            else:
                print("Will NOT clear the folder before proceeding.")
                print("The folder may contain more and other data than expected.")


def copy_from_folder_to_folder(source_folder, destination_folder):
    """
    Use os-specific shell commands to recursively copy folder content to destination folder

    Parameters
    ----------
    """
    if is_linux():
        subprocess.run(
            ["cp", "-R", os.path.join(source_folder, "."), destination_folder]
        )
    else:
        subprocess.run(["xcopy", "/s", source_folder, destination_folder])


def copy_file(source_file, destination):
    """
    Use os-specific shell commands to copy source_file to destination

    Parameters
    ----------
    """
    if is_linux():
        subprocess.run(["cp", source_file, destination])
    else:
        subprocess.run(["xcopy", "/y", source_file, destination])
