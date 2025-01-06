#!/usr/bin/env python
# coding: utf-8

# #  ISD History Station Table
# This script parses the Integrated Surface Database Station History 'isd-history.txt' file and returns:<BR>
# 1. .csv table containing the columns below
# 2. 'isd history definitions' containing all non-tabular data  
#     
# The table is used to lookup station details from a USAF id number.  The 'isd history definitions' is saved as a .txt file.
# 
# __Columns:__<BR>
#  USAF = Air Force station ID. May contain a letter in the first position.<BR>
#  WBAN = NCDC WBAN number<BR>
#  CTRY = FIPS country ID<BR>
#    ST = State for US stations<BR>
#  ICAO = ICAO ID<BR>
#   LAT = Latitude in thousandths of decimal degrees<BR>
#   LON = Longitude in thousandths of decimal degrees<BR>
#  ELEV = Elevation in meters<BR>
# BEGIN = Beginning Period Of Record (YYYYMMDD). There may be reporting gaps within the P.O.R.<BR>
#   END = Ending Period Of Record (YYYYMMDD). There may be reporting gaps within the P.O.R.<BR>
# 
# This script is intended to be executed on initial setup and updated periodically.
# 
# __source:__ https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt

# __USAF   WBAN__  STATION NAME                  CTRY ST CALL  LAT     LON      ELEV(M) BEGIN    END
# 
# __722190 13874__ HARTSFIELD-JACKSON ATLANTA IN US   GA KATL  +33.630 -084.442 +0308.3 19730101 20241215

from pandas import DataFrame, to_datetime
from urllib.request import urlopen
from pathlib import Path

# single source of input
target_url = 'https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt'
# read URL
data = urlopen(target_url)
txt = data.read()
# make sure it's not empty
assert txt.__len__() > 10000

lines = [x_.strip() for x_ in str(txt).split('\\n')]
# remove 'b' character from start of line 0
lines = [lines[0][2:]] + lines[1:]

# find table header - this defines the start of the table as well as the split 
# for the two files output in this script.
str_header = 'USAF   WBAN  STATION NAME'
# what is the line index that starts with 'str_header'?
idx_header = [idx_ for idx_, x_ in enumerate(lines) if x_.startswith(str_header)][0]

line_header = lines[idx_header]
assert line_header.startswith(str_header)

# create isd_history_defintions_txt containing all lines of text up to idx_header (ie.,
# the first half of the document)
isd_history_defintions_txt = '\n'.join(lines[:idx_header])
# print(isd_history_defintions_txt)

# Open the file in write mode
dir_cwd = Path.cwd()
with open(dir_cwd / "isd_history_defintions.txt", "w") as file:
  # Write the text to the file
  file.write(isd_history_defintions_txt)

# the rest of the script is for the isd-history.csv table only

# identify column names
# 'STATION NAME' is a single name, not two
col_names = [x_.strip() for x_ in line_header.split(' ') if x_ != '']
col_names = [x_.replace('NAME', '').replace('STATION', 'STATION NAME') for x_ in col_names]
col_names.remove('')

# identify separators (necessary because many lines do not provide all values for all columns)
line_header_pad = line_header + ' '
col_separators = [line_header_pad.index(f'{x_} ') for x_ in col_names]
assert len(col_names) == len(col_separators)
# to check for strictly increasing list
assert all(i < j for i, j in zip(col_separators, col_separators[1:]))

col_name_separators = dict(zip(col_names, col_separators))

# extract lines for table section of document only
lines_table = [x_ for x_ in lines[idx_header +1:] if x_ != '']

separators_start_end = list(zip(col_separators, col_separators[1:] + [500]))

# Split lines into columns
records = []
for line_ in lines_table:
    row = []
#     list of separators start
    for start_, end_ in separators_start_end:
#         find the term between the start and end indices and strip leading/trailing whitespaces
        term_ = line_[start_:end_].strip()
        row.append(term_.strip())
    records.append(row)

# store records in a dataframe
df = DataFrame.from_records(records, columns=col_names)

# ### Remove records with neither a 'WBAN' or 'CALL' value
# non-USA locations that can be referenced using 'CALL'
# USA locations use WBAN
filter_wban = df['WBAN'].ne('99999')
filter_call = df['CALL'].str.strip().str.len().eq(4)
filter_wban_or_call = filter_wban | filter_call
# df = df.loc[filter_wban]
df = df.loc[filter_wban_or_call]

# ### Format 'BEGIN', 'END' as datetime
# discard rare non-conforming values
cols_datetime = df.columns.intersection(['BEGIN', 'END'])
for col_ in cols_datetime:
#     for values with whitespaces, choose the second group as input
    df[col_] = to_datetime(df[col_].str.split().str[-1], errors='coerce')

#     important that 'CALL' and 'WBAN' have no whitespaces
df['CALL'] = df['CALL'].str.strip()
df['WBAN'] = df['WBAN'].str.strip()
df = df.sort_values(by=['USAF', 'BEGIN'], ascending=[True, False])
df.set_index('USAF', drop=True, inplace=True)
df.dropna(subset = ['BEGIN','END'], how='all', inplace=True)
# #### Reduce df to only locations with a non 99999 WBAN value - DON'T use
# this excludes non-USA locations.
# filter_wban_99999 = df['WBAN'].eq('99999')
# display(df.shape)
# df = df.loc[~filter_wban_99999]

# save as 'isd_history.csv' to cwd (this avoids overwriting existing in 'data' but 
# requires manually moving the file(s) after completion)
df.to_csv(dir_cwd / "isd-history.csv")
# END

