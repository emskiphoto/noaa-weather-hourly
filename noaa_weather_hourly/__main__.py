#!/usr/bin/env python
# coding: utf-8

# # noaa_weather_hourly
# This script cleans and formats a manually downloaded National Oceanic and Atmospheric Administration (NOAA) Local Climatological Data (LCD) CSV weather file.  
#     
# Copyright Matt Chmielewski<BR>
# https://github.com/emskiphoto/noaa_weather_hourly
# January 10, 2025
# Load Pandas
import pandas as pd
# Load pure Python packages
import argparse
import csv
import pathlib
import re
# to read resources from the directories of this package
import importlib.resources
# import modules specific to this package 
from config import *
from utils import *

# Capture command line arguments
parser = argparse.ArgumentParser(description="""noaa_weather_hourly - for processing raw NOAA LCD observed weather .csv files.

# Usage for specific file:
Process the version 1 LCD file "./data//3876540.csv" that is included in installation.
$ noaa_weather_hourly -filename "./data//3876540.csv"
""")

# optional argument 'filename' - if not supplied, script will search for files by pattern
parser.add_argument('-filename', help='File path to NOAA LCD CSV file to be processed (ie. "data/3876540.csv").  File path input is only needed to process files in other directories, otherwise the most recent file(s) in the current directory will be detected automatically.')
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
    
# ## Locations
# dir_cwd is where the command was entered and where files will be output to
dir_cwd = pathlib.Path.cwd()

# #### Are there any .CSV files of any naming format?
# If not, stop the script, there is nothing to do without the local .csv's.
# pretty name of directory
dir_cwd_posix = dir_cwd.as_posix()

# this is the dir where input files will be read from.  It will be defined as
# either dir_cwd or dir_filename based on the outcome of the next steps
dir_source = None
dir_filename = None
# if 'filename' was provided, use filename. if 'filename' was not provided, 
# review available .csv's in dir_cwd. if some .csv files are present, continue.  
# Otherwise halt process and inform user.
if filename == '':
    dir_source = dir_cwd
    dir_source_posix = dir_source.as_posix()
    dir_csv_files = sorted([f_.name for f_ in dir_source.glob('*.csv') if f_.is_file()])
    if len(dir_csv_files) >= 1:
        pass
        # list of all .csv files in dir_cwd
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


# which files matched lcd patterns, regardless of version or date?
files_pattern_match = [x for xs in version_files.values() for x in xs]

# what if no files were found? or one file? return message and halt process
if len(files_pattern_match) < 1:
    message_ = message_no_lcd_files_found.format(dir_source_posix = dir_source_posix,
                                 patterns_lcd_examples_str = patterns_lcd_examples_str,
                                dir_csv_files_str = dir_csv_files_str)
    print(message_)
#     abort process
    exit()

# find most recently modified file by lcd version number
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

# read headers only of each file in files_lcd_input
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
# print(files_usecols)

# ### Create df from files_usecols
df = pd.concat((pd.read_csv(f_, usecols=cols_, parse_dates=['DATE'],
                            index_col='DATE', low_memory=False) for
                f_, cols_ in files_usecols.items()), axis=0)\
                .reset_index().drop_duplicates()
df = df.set_index('DATE', drop=True).sort_index()

# individually process all columns in df to be numeric --> float
cols_numeric_stats = df.columns.difference(cols_sunrise_sunset + cols_date_station)
for col_ in cols_numeric_stats:
# for col_ in df.columns:
    df[col_] = pd.to_numeric(df[col_], errors='coerce')
    try:
        df[col_] = df[col_].astype(float)
    except:
        pass

# keep track of the count of raw timestamps prior to processing
n_records_raw = df.shape[0]
# track statistics by column prior to processing, omit 'Sunrise' & 'Sunset' from stats
cols_sunrise_sunset = df.columns.intersection(cols_sunrise_sunset).tolist()
df_stats_pre = df.loc[:, cols_numeric_stats].describe()

# ### Identify and Display Weather Station Information
# use most frequent STATION id from df
station_lcd = str(df['STATION'].value_counts().index[0])
# v1 - identify WBAN station - this is index for the isd-history table
station_wban = station_lcd[6:]
# v2 - identify CALL station  - needed for non-USA locations with 99999 WBAN
station_call = station_lcd[-4:] 

# remove 'STATION', 'REPORT_TYPE', 'SOURCE' columns - not needed anymore
df.drop(columns=['STATION', 'REPORT_TYPE', 'SOURCE'],
        inplace=True, errors='ignore')

# #### Open local 'isd-history.csv' containing Station location/identification
# information stored in 'data' folder.  source:  https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt.  Created/updated manually with 'ISD History Station Table.py'.

# print(list(pathlib.Path.cwd().glob('*')))
dir_data = dir_cwd / 'noaa_weather_hourly/data'

# path_isd_history = dir_data / file_isd_history
# # assert path_isd_history.is_file()
# # # #### Create df_isd_history for Station Detail lookup
# df_isd_history = pd.read_csv(path_isd_history, index_col='WBAN',
#                      dtype={'WBAN': object}).sort_values(
#                     by=['USAF', 'BEGIN'], ascending=[True, False])

# NEED TO FIGURE OUT HOW TO USE IMPORTLIB.RESOURCES!!
# # # Access a file in the noaa-weather-history package 'data' directory (not a relative, local, 'data' dir)
def read_isd_history(file):
    """Read isd-history CSV file from 'data' directory of Python package."""
#     data_res = importlib.resources.files("noaa_weather_hourly") / "data"
    data_res = importlib.resources.files("noaa_weather_hourly") / "data"
    with importlib.resources.as_file(data_res / file) as f:
        df = pd.read_csv(f)
    return df

df_isd_history = read_isd_history(file_isd_history)

# def read_csv_from_package(package_name, resource_name):
#     """Reads a CSV file from a Python package using importlib.resources."""

#     with importlib.resources.open_text(package_name, resource_name) as f:
#         return pd.read_csv(f)
#         reader = csv.reader(f)
#         for row in reader:
#             print(row)

# Example usage:
# df_isd_history = read_csv_from_package("noaa_weather_hourly", file_isd_history)


# with importlib_resources.files("noaa_weather_hourly") / "data" / file_isd_history as isd_history:
    


# with importlib.resources.path("noaa_weather_hourly-cli.data", file_isd_history) as data_isd_history_path:
#     with open(data_isd_history_path, 'r') as f:
# #         reader_isd = csv.reader(f)
#         df_isd_history = pd.read_csv(f, index_col='WBAN',
#                      dtype={'WBAN': object}).sort_values(
#                     by=['USAF', 'BEGIN'], ascending=[True, False])


# is the station WBAN listed in df_isd_history?
station_details_available_wban = station_wban in df_isd_history.index

# is the station CALL listed in df_isd_history?
station_details_available_call = station_call in df_isd_history['CALL'].values

# create station_details using either WBAN or CALL as index lookup
if station_details_available_wban:
    station_details = dict(df_isd_history.loc[station_wban].reset_index()\
                       .sort_values('END', ascending=False).iloc[0])
elif station_details_available_call:
    station_details = dict(df_isd_history.loc[
                        df_isd_history['CALL'] == station_call]\
                       .reset_index().sort_values('END',
                          ascending=False).iloc[0])
else:
#     if station_lcd has no reference in df_isd_history...create empty dictionary
    station_details = {col_ : 'Unknown' for col_ in df_isd_history.columns}

# add google maps url to LAT LON
if station_details['LAT'] != 'Unknown':
     # add url to google maps search of lat, lon values to station_details
    station_details['GOOGLE MAP'] = google_maps_url(station_details['LAT'],
                                                    station_details['LON'])

# delete df_isd_history - no longer needed
del df_isd_history
    
#     create timestamps from consolidated table df
start_dt = df.index[0]
end_dt = df.index[-1]
start_str = start_dt.strftime('%Y-%m-%d')
end_str = end_dt.strftime('%Y-%m-%d')

# identify hourly timestamps where the LCD source reported no observations
# This will be added as a boolean column later
idx_hours_no_source_data = pd.date_range(start_dt, end_dt, freq='H')\
                            .difference(df.index.round('H'))
# how many hours of the curent time range have no observations?
n_hours_no_source_data = len(idx_hours_no_source_data)

# individually process all columns in df to be numeric --> float - MOVED TO ABOVE
# for col_ in df.columns:
#     df[col_] = pd.to_numeric(df[col_], errors='coerce')
#     try:
#         df[col_] = df[col_].astype(float)
#     except:
#         pass
    
 # if a single timestamp appears more than once, average available values
# to return a single value and single timestamp (ignoring 
# NaN values of course)
df = df.groupby(level=0).mean()

# #### Extract Sunrise and Sunset by date in to dictionaries
# dicionaries to be applied to df_out towards end of script.
# The source data provides only one unique sunrise/set value per day and
# the rest of the day's values are NaN

# create date_sunrise/sunset dictionaries with dates as keys and 
# timestamp values for time to be added back in to resampled df
# date_sunrise = datetime_from_HHMM(df['Sunrise'].dropna()).to_dict()
# date_sunset = datetime_from_HHMM(df['Sunset'].dropna()).to_dict()

# # create date_sunrise/sunset dictionaries with dates as keys and 
# # timestamp values for time to be added back in to resampled df
temp_sunrise = df['Sunrise'].dropna()
temp_sunrise.index = temp_sunrise.index.floor('D')
date_sunrise = datetime_from_HHMM(temp_sunrise).to_dict()
del temp_sunrise

temp_sunset = df['Sunset'].dropna()
temp_sunset.index = temp_sunset.index.floor('D')
date_sunset = datetime_from_HHMM(temp_sunset).to_dict()
del temp_sunset

# drop sunrise/sunset columns as their information is now 
# contained in the date_sunrise/sunset dictionaries
df.drop(columns=cols_sunrise_sunset, inplace=True, errors='ignore')

# #### are there timestamps that have a high count of null values?
# In v1 LCD files the '23:59:00' timestamp is suspect and appears to only be a placeholder
# for posting sunrise/sunset times.  Important that this step be done after
# forward filling sunrise/sunset values. 
# V2 LCD files do not seem to have the '23:59:00' timestamp issue.

n_max_null = int(pct_null_timestamp_max * df.shape[0])

temp = df.loc[:, df.columns.difference(cols_sunrise_sunset)]
df_nan_ts = temp.groupby(temp.index.time).apply(lambda x: x.isna().sum()\
                            .gt(n_max_null)).all(axis=1)
times_nan = df_nan_ts.loc[df_nan_ts].index.tolist()
del temp
del df_nan_ts

# remove records for timestamps with a high percentage of Null values.
# note that the '23:59:00' timestamp is suspect and appears to only be a placeholder
# for posting sunrise/sunset times.  Important that this step be done after
# forward filling sunrise/sunset values.
filter_nan_times = pd.Series(df.index.time).isin(times_nan).values
df = df.loc[~filter_nan_times]

#     Check what percentage of data has null data and print to screen
df_pct_null_data = pd.DataFrame({'% NaN - Source': df.isnull().sum().divide(len(df)).round(4)})
df_pct_null_data_pre_formatted = df_pct_null_data['% NaN - Source']\
                            .apply(lambda n: '{:,.2%}'.format(n))
# remove 'Hourly' prefix for display only
col_rename_remove_hourly = {col_ : col_.replace('Hourly', '') for
                            col_ in df_pct_null_data_pre_formatted.index}

# #### Display Station Details
# exclude station lifetime BEGIN, END history dates - could cause confusion
station_details_exclude = ['BEGIN', 'END']
station_details_display = {k_ : v_ for k_, v_ in station_details.items() if
                           k_ not in station_details_exclude}

print('--------------------------------------------')
print('------ ISD Weather Station Properties ------')
print('--------------------------------------------')
for k_, v_ in station_details_display.items():
    print("{:<15} {:<10}".format(k_, v_))
print('\n')

# ### Resample Hourly
# individually resample each column on an hourly frequency.
# This will produce series
# with perfect, complete datetime indexes.  However, it is quite
# possible that NaN values will remain (ie. a contiguous 3-hour
# period of NaN values).  Remaining NaN values will
# be resolved through interpolation later in the script.
# this method is used because NaN values can appear at different timestamps
# in each column
# at this point the df should contain only numeric data
dfs = {}
for col_ in df.columns:
    dfs[col_] = df[col_].dropna().resample('H').mean()
    
# ### Create df_out - the beginning of the final output
# join the resampled series from the previous step, remove any
# duplicates and ensure the index is recognized as hourly frequency.
# df_out = pd.concat(dfs, axis=1).drop_duplicates().asfreq('H')
# important to enforce dtype 'float' as 'HourlyRelativeHumidity' and 
# other columns had a 'Float64' (capital 'F') that generated
# errors in interpolation step.
df_out = pd.concat(dfs, axis=1).drop_duplicates()\
                .asfreq('H').astype(float)
del dfs
del df

# ### Interpolate Null Values
# According to the following parameters:
# Because observed weather data commonly contains gaps (ie., NaN or null values), noaa_weather_hourly will attempt to fill in any such gaps to ensure that in each record a value is present for all of the hourly timestamps. To do so, it will use time-based interpolation for gaps up to a default value of 24 hours long ('max_records_to_interpolate').  For example if the dry bulb temperature has a gap with neighboring observed values like (20, X, X, X, X, 25), noaa_weather_hourly will replace the missing values to give (20, 21, 22, 23, 24, 25).
# 
# If a gap exists in the data that is larger than max_records_to_interpolate, NaN values will be left untouched and a complete datetime index will be preserved.
df_out = df_out.interpolate(method='time',
            limit = max_records_to_interpolate)

# ### Optional Frequency Resample
# If the freqstr is not 'H', resample.  
run_resample = False
# If the freqstr is not the default 'H', run the resample process
if freqstr != 'H':
    run_resample = True
# If the input freqstr is higher than 'H', resample and interpolate, else resample using mean.
resample_interpolate = False
#     what is the delta value of the input freqstr? 
freqstr_delta = pd.date_range(start_dt, periods=100,
                           freq=freqstr).freq.delta

# If the input freqstr is higher frequency 
# than df_out, resample using interpolation
resample_interpolate = freqstr_delta < df_out.index.freq.delta

# shall we proceed with additional resampling?
if run_resample:
    if resample_interpolate:
        #     resample via interpolation
        df_out = df_out.resample(freqstr).interpolate()
# or resample using mean
    elif not resample_interpolate:
        df_out = df_out.resample(freqstr).mean()
    
# ### Pre- Post-Processing Statistical Comparison
# create general statistics on post-processed dataset for
# comparison with pre-processed dataset to understand how/if 
# processing significantly altered series values
df_stats_post = df_out[df_stats_pre.columns].describe()
# Create df_mean_comp containing comparison of mean values of source and processed numeric columns 
df_mean_comp = pd.concat([df_stats_pre.loc['mean'].T, df_stats_post.loc['mean'].T],
                         axis=1, keys=['Source Mean', 'Processed Mean']).round(2)\
                            .rename(index=col_rename_remove_hourly)
df_mean_comp['% Difference'] = df_mean_comp.pct_change(axis=1).iloc[:,-1]\
                                .fillna(0).round(4)\
                                .apply(lambda n: '{:,.2%}'.format(n))

#     Check what percentage of data has null data and print to screen
df_pct_null_data_post = pd.DataFrame({'% NaN - Processed': df_out.isnull()\
                              .sum().divide(len(df_out)).round(4)})
df_pct_null_data_post_formatted = df_pct_null_data_post['% NaN - Processed']\
                                .apply(lambda n: '{:,.2%}'.format(n))
# print(df_pct_null_data_post_formatted.rename(
#                 index = col_rename_remove_hourly))
# Create df_pct_null_comp containing comparison of pct null values before and after processing
df_pct_null_comp = pd.concat([df_pct_null_data_pre_formatted, 
                             df_pct_null_data_post_formatted], 
                            axis=1).rename(index=col_rename_remove_hourly)

# Create df_comp containing pct null and mean values
df_comp = df_pct_null_comp.join(df_mean_comp)

message_ = message_pct_null_data.format(
                files_lcd_input_names_str = files_lcd_input_names_str,
                start_str = start_str,
                end_str = end_str)
print(message_)

print('----------------------------------------------------------------')
print('---- Percent Null Values by Column:  Source vs Processed ------')
print('----------------------------------------------------------------')
# print(df_pct_null_comp)
print(df_comp)

# Round df_out to 1 decimal place
df_out = df_out.round(2)

# ### Add Sunrise/Sunset timestamps to df_out
# apply date_sunrise/sunset dictionary to df_out index to create sunrise/sunset columns
for col_, dict_ in zip(cols_sunrise_sunset, [date_sunrise, date_sunset]):
    if len(dict_) > 1:
        df_out[col_] = pd.DataFrame.from_dict(dict_, orient='index')\
                    .reindex(df_out.index).ffill().astype('datetime64[s]')
    else:
        df_out[col_] = pd.NaT
# cleanup
del date_sunrise, date_sunset

# add column to document hourly obervations where no source data was provided.
df_out['No source data'] = df_out.index.isin(idx_hours_no_source_data)

# #### Rename Columns - remove 'hourly' from names
df_out.rename(columns=col_rename_remove_hourly, errors='ignore',
             inplace=True)

# #### Name export file 
# Save output file to current working directory (ie,
# where command line command was entered).  Revise STATION NAME to permit save to disk on typical OS.
file_out_name = file_output_format.format(
            STATION_NAME = slugify(station_details['STATION NAME']),
            start_str = start_str,
            end_str = end_str,
            freqstr = freqstr)
file_out = dir_cwd / file_out_name
# what if file name is too long for current OS? - TO-DO
# file_out.as_posix().__len__()

# #### Save df_out to csv as file_out
df_out.to_csv(file_out)
assert file_out.is_file()
print(f"""\nProcessed File Saved to: {file_out.as_posix()}\n
{''.join(80 * ['*'])}
          ***************       PROCESS COMPLETE       ***************
{''.join(80 * ['*'])}""")
# ### Cleanup
del df_out
exit()
