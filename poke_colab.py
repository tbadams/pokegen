from datetime import datetime
import os
from os import listdir
from os.path import isfile, join
import shutil
import time

try:  # if in Google Colaboratory
    import gpt_2_simple as gpt2
    from google.colab import drive
    from google.colab import files
except:
    pass

# files
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
    if  overwrite or not os.path.isfile(os.path.join(DRIVE_ROOT, fname)):
      print("copied {}".format(fname))
      shutil.copyfile(fname, DRIVE_ROOT + fname)
    else:
      print("skipped {}".format(fname))
