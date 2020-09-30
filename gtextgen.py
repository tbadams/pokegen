import os
from os import path
import re
import json


SAMPLE_DATA_FILE_NAME = "poke_data.txt"

if not path.exists(SAMPLE_DATA_FILE_NAME):
    raise FileNotFoundError("Need data!")
file_name = SAMPLE_DATA_FILE_NAME
cur_run = "gpoke4d"
