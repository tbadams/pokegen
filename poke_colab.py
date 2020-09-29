from datetime import datetime
import os
from os import listdir, path, makedirs
import shutil
import time
import tarfile

try:  # if in Google Colaboratory
    import gpt_2_simple as gpt2
    from google.colab import drive
    from google.colab import files
except:
    pass

# files
BIN_OUT_DIR = "bin"
TAR_FILE_NAME = "pokegen_lib.tar"
SAMPLE_DATA_FILE_NAME = "poke_data.txt"

DRIVE_ROOT = "/content/drive/My Drive/"
# text
START_TOKEN = "<|startoftext|>"
END_TOKEN = "<|endoftext|>"

BS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def to_base(s, b):
    res = ""
    while s:
        res += BS[s % b]
        s //= b
    return res[::-1] or "0"


def all_to_gdrive(fnames, overwrite=False):
    for fname in fnames:
        if overwrite or not os.path.isfile(os.path.join(DRIVE_ROOT, fname)):
            print("copied {}".format(fname))
            shutil.copyfile(fname, DRIVE_ROOT + fname)
        else:
            print("skipped {}".format(fname))


def package_colab_resources(filename=TAR_FILE_NAME):
    with tarfile.open(filename, "w") as tar:
        tar.add(SAMPLE_DATA_FILE_NAME)
        tar.add(path.basename(__file__))

# FIRST, get data, code we need
# TAR_FILE_NAME = "pokegen_lib.tar"
# if not path.exists(TAR_FILE_NAME):
#   uploaded = files.upload()
# if not path.exists(TAR_FILE_NAME):
#   raise FileNotFoundError("Need data, library!")
# with tarfile.open(TAR_FILE_NAME, "r") as tar:
#   tar.extractall()
# import poke_colab as poke
