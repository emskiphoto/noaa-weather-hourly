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




# this is the dir where input files will be read from.  It will be defined as
# either dir_cwd or dir_filename based on the outcome of the next steps
dir_source = None
dir_filename = None
# if 'filename' was provided, use filename.
# if 'filename' was not provided, review available .csv's in dir_cwd.
# if some .csv files are present, continue.  
# Otherwise halt process and inform user.
if filename == '':
    dir_source = dir_cwd
    dir_source_posix = dir_source.as_posix()
    dir_csv_files = sorted([f_.name for f_ in dir_source.glob('*.csv') if f_.is_file()])
    if len(dir_csv_files) >= 1:
#         dir_source = dir_cwd
        pass
        # list of all .csv files in dir_cwd
#         dir_csv_files = sorted([f_.name for f_ in dir_cwd.glob('*.csv') if f_.is_file()])
    else:
        message_ = message_no_csv_files_found.format(
            dir_source_posix = dir_cwd_posix)
        print(message_)
#  if user inputs a -filename argument..
elif filename != '':
    filename_path = pathlib.Path(filename)
    if filename_path.is_file():
        dir_source = filename_path.parent
        dir_source_posix = dir_source.as_posix()
        # list of all .csv files in dir_filename
        dir_csv_files = sorted([f_.name for f_ in dir_source.glob('*.csv') if f_.is_file()])
    else:
        dir_csv_files = []
        print(f'{filename} is not a valid file')
    
# string version of list of all csv files
dir_csv_files_str = ', '.join(dir_csv_files)

# print all available csv files
print(message_all_csv_files_found.format(
        dir_source_posix = dir_source_posix,
        dir_csv_files_str = dir_csv_files_str))

# ### Locate LCD .CSV file(s) 'files_lcd_input'
# This script is intended to be executed from a terminal command line.  The LCD input file(s) are expected to be saved in the same directory that the command line is executed in.  The file name(s) are expected to match the pattern associated with multiple LCD file versions in 'patterns_lcd_input_files' (two versions currently).  However, if a file(s) with this pattern is not identifed, do NOT attempt to use any non-matching .CSV file in the same directory.  Inform user that no matching file was found and no files will be opened or created.
# 
# The benefits of this approach are:
# 1. code will not mistakenly use non-LCD files
# 2. User can be sloppy (or organized) with their LCD file storage.  New source files and output files can simply be accumulated in the same folder with no data loss.
# 3. Simple command line requires no mandatory input, only optional frequency and parameter setting inputs.

# ### which version of LCD files are avaialble and which are the most recent?
# 1. find all files that match v1 or v2 naming
# 2. find the most recent file
# 3. Determine if most recent file is v1 or v2 format 'lcd_version'
# 4. see if there is more than one file with the same station ID
# 5. create list 'files_lcd' with one or more lcd files of same station id 

# 1. find all files that match v1 or v2 naming and sort by last modified date descending
# create 'version_files' dictionary with LCD version number as key and list of matching 
# files as values
version_files = {v_ : find_files_re_pattern_sorted_last_modified(dir_source, pattern_) for
                 v_, pattern_ in version_pattern_lcd_input.items()}

# what if no files were found? or one file? 
# return message and halt process
# which files matched lcd patterns, regardless of version or date?
files_pattern_match = [x for xs in version_files.values() for x in xs]

if len(files_pattern_match) < 1:
    message_ = message_no_lcd_files_found.format(dir_source_posix = dir_source_posix,
                                 patterns_lcd_examples_str = patterns_lcd_examples_str,
                                dir_csv_files_str = dir_csv_files_str)
    print(message_)
#     abort process
    exit()

# find most recently modified file by lcd version
version_file_last_modified = {version_ : files_[0] if len(files_) > 0 else None for version_, files_ in version_files.items()}

# 2. find the most recent file
file_last_modified = sorted([(f, f.stat().st_mtime) for
                  f in version_file_last_modified.values() if f != None],
           key=lambda x: x[1], reverse=True)[0][0]
# 3. Determine if most recent file is v1 or v2 format 'lcd_version'
# versions start with '1' so need to add 1 to zero-indexed list
lcd_version = list(version_file_last_modified.values())\
                            .index(file_last_modified) + 1

# make sure we have the right version
assert file_last_modified in version_files[lcd_version]

# 4. see if there is more than one file that has the same station ID
# as found in 'file_last_modified'
# This requires extraction of a unique identifier in LCD file name that is common to
# other LCD files for same location (but probably different dates).  

# Note that only the LCD v2 files need to be grouped.  LCD v1 files are 
# delivered with multi-year date ranges (if requested) while LCD v2
# files are for discrete calendar years (or less), for example 'LCD_USW00014939_2020.csv'.  

# Grouping LCD v1 files could be implemented, but this would require cooperation
# from the user in terms of renaming the LCD v1 files in a specific format.
# LCD v1 files are delivered with the same name ('3876540.csv') regardless
# of the number of calendar years in the time range of the data in file.    

# files_lcd_input - empty list to hold final, qualified selection of LCD input files
files_lcd_input = []
# different treatment for v2 LCD files
if lcd_version == 2:
# extract id_file_lcd2 as the blob of characters between first and second '_'
# reference 'LCD_USW00014939_2023.csv' --> 'USW00014939'
    id_file_lcd2 = file_last_modified.name.split('_')[1]
#     which files contain id for the current lcd_version?
    files_ = [file_ for file_ in version_files[lcd_version] if id_file_lcd2 in file_.name]
    files_lcd_input.extend(files_)
#     print('v2')
else:
#     this is a v1 file and therefore a single comprehensive file
    files_lcd_input.append(file_last_modified)

# string version of filenames from files_lcd_input as vertical list
files_lcd_input_names_str = "\n".join([f_.name for f_ in files_lcd_input])

# read only headers of each file in files_lcd_input
files_columns = {}
for file_ in files_lcd_input:
    try:
#         this is 30x faster than pd.read_csv(file_, index_col=0, nrows=0).columns.tolist()
        with open(file_, 'r') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
        files_columns[file_] = sorted(fieldnames)
    except:
        continue

# ### Create files_usecols containing validated files and columns to be used
# _validation steps for each file:_
# * is their a 'DATE' column?
# * is at least one of the `cols_data` columns available?
# * keep only columns found in `cols_noaa_processed`

# #### Is 'DATE' available for every file in files_lcd_input?
# keep only files that have a 'DATE' column - otherwise where is this data supposed to go?
files_usecols = {file_ : cols_ for file_, cols_ in files_columns.items()
                 if 'DATE' in cols_}
# #### Keep only files that have at least one cols_data column
files_usecols = {file_ : cols_ for file_, cols_ in files_usecols.items()
                 if len(set(cols_).intersection(set(cols_data))) >=1}
# reduce files_usecols to only columns used in this process
files_usecols = {file_ : sorted(set(cols_noaa_processed).intersection(set(cols_))) for
                 file_, cols_ in files_usecols.items()}
print(files_usecols)




