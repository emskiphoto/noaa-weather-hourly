#!/usr/bin/env python
# coding: utf-8

# # noaa-weather-hourly
# This script cleans and formats a manually downloaded National Oceanic and Atmospheric Administration (NOAA) Local Climatological Data (LCD) CSV weather file.  
#     
# Copyright Matt Chmielewski<BR>
# https://github.com/emskiphoto/noaa-weather-hourly
# January 6, 2025

# Load Python packages
import argparse
import pandas as pd
import csv
import pathlib
import re
import importlib.resources
# import modules specific to this package 
from config import *
from utils import *

# Capture command line arguments
parser = argparse.ArgumentParser(description='noaa-weather-hourly - for processing raw NOAA LCD observed weather .csv files.  Execute this command in a directory containing files to be processed')
# optional argument 'filename' - if not supplied, script will search for files by pattern
parser.add_argument('-filename', help='File path to NOAA LCD CSV file to be processed (ie. "data/test_file_lcd1.csv").  File path input is only needed to process files in other directories, otherwise the most recent file(s) in the current directory will be detected automatically.')
# optional argument 'frequency' - default is 'H' (hourly).  If -frequency is provided
parser.add_argument('-frequency', type=str, help=f'Time frequency of output CSV file {freqstr_frequency}.  Multiples of frequency values may also be used, for example "15T": 15-minute frequency.')

args = parser.parse_args()

# TEST - is utils.py import functional?
# say_hello()
# TEST - is config.py import functional?
# print(freqstr_frequency)
# TEST
# try:
#     print(args.filename)
# except:
#     pass

# overwrite default 'freqstr' if frequency was provided in command line arg
if args.frequency != None:
    freqstr = args.frequency

# overwrite default 'filename' if filename was provided in command line arg
if args.filename != None:
    filename = args.filename
    
# print(freqstr)

# ## Locations
# dir_cwd is where the command was entered and where files will be output to
dir_cwd = pathlib.Path.cwd()

# # Access a file in the data directory
# with importlib.resources.path("your_package.data", "data_file.txt") as data_file_path:
#     with open(data_file_path) as f:
#         data = f.read()

# #### Are there any .CSV files of any naming format?
# If not, stop the script, there is nothing to do without the local .csv's.
# pretty name of directory
dir_cwd_posix = dir_cwd.as_posix()


# if 'filename' was provided, use filename.
# if 'filename' was not provided, review available .csv's in dir_cwd.
# if some .csv files are present, continue.  
# Otherwise halt process and inform user.
dir_filename = None
if filename == '':
    dir_csv_files = sorted([f_.name for f_ in dir_cwd.glob('*.csv') if f_.is_file()])
    if len(dir_csv_files) >= 1:
        pass
        # list of all .csv files in dir_cwd
#         dir_csv_files = sorted([f_.name for f_ in dir_cwd.glob('*.csv') if f_.is_file()])
    else:
        message_ = message_no_csv_files_found.format(
            dir_cwd_posix = dir_cwd_posix)
        print(message_)
elif filename != '':
    filename_path = pathlib.Path(filename)
    if filename_path.is_file():
        dir_filename = filename_path.parent
        dir_filename_posix = dir_filename.as_posix()
        # list of all .csv files in dir_filename
        dir_csv_files = sorted([f_.name for f_ in dir_filename.glob('*.csv') if f_.is_file()])
    else:
        dir_csv_files = []
        print(f'{filename} is not a valid file')
    
# string version of list of all csv files
dir_csv_files_str = ', '.join(dir_csv_files)

# print all available csv files
print(message_all_csv_files_found.format(
        dir_posix = dir_filename if dir_filename != None else dir_cwd_posix,
        dir_csv_files_str = dir_csv_files_str))

