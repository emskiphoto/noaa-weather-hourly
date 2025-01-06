#!/usr/bin/env python
# coding: utf-8

# # noaa-weather-hourly
# This script cleans and formats a manually downloaded National Oceanic and Atmospheric Administration (NOAA) Local Climatological Data (LCD) CSV weather file.  
# 
# This is the jupyter notebook development version of the script.  This script is converted to a .py file in the final published version.
# 
#  __Originated From:__
# https://github.com/emskiphoto/Process-historical-NOAA-LCD-weather<BR>
#     
# Copyright Matt Chmielewski<BR>
# https://github.com/emskiphoto/noaa-weather-hourly<BR>
# January 6, 2025



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

# In[41]:


# 1. find all files that match v1 or v2 naming and sort by last modified date descending
# create 'version_files' dictionary with LCD version number as key and list of matching 
# files as values
version_files = {v_ : find_files_re_pattern_sorted_last_modified(dir_data, pattern_) for
                 v_, pattern_ in version_pattern_lcd_input.items()}
version_files


# In[42]:


# what if no files were found?  
# return message and halt process
# which files matched lcd patterns, regardless of version or date?
# files_pattern_match = [x for xs in version_files.values() for x in xs]
files_pattern_match = [x for xs in version_files.values() for x in xs]
try:
    assert len(files_pattern_match) >= 1
except:
    message_ = message_no_lcd_files_found.format(dir_cwd_posix = dir_cwd_posix,
                                 patterns_lcd_examples_str = patterns_lcd_examples_str,
                                dir_cwd_csv_files_str = dir_cwd_csv_files_str)
    print(message_)
#     assert
    raise


# In[43]:


# find most recently modified file by lcd version
version_file_last_modified = {version_ : files_[0] for version_, files_ in version_files.items()}
version_file_last_modified


# In[44]:


# 2. find the most recent file
file_last_modified = sorted([(f, f.stat().st_mtime) for
                  f in version_file_last_modified.values()],
           key=lambda x: x[1], reverse=True)[0][0]
# 3. Determine if most recent file is v1 or v2 format 'lcd_version'
# versions start with '1' so need to add 1 to zero-indexed list
lcd_version = list(version_file_last_modified.values())\
                            .index(file_last_modified) + 1
# file_last_modified, lcd_version


# In[45]:


# make sure we have the right version
assert file_last_modified in version_files[lcd_version]


# ### Group LCD .CSV input file(s) as 'files_lcd_input'

# In[46]:


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
# of date range of data in file.    


# In[47]:


# files_lcd_input - empty list to hold final, qualified selection of LCD input files
files_lcd_input = []
# different treatment for v2 LCD files
if lcd_version == 2:
# extract id_file_lcd2 as the blob of characters between first and second '_'
# reference 'LCD_USW00014939_2023.csv'
    id_file_lcd2 = file_last_modified.name.split('_')[1]
#     which files contain id for the current lcd_version?
    files_ = [file_ for file_ in version_files[lcd_version] if id_file_lcd2 in file_.name]
    files_lcd_input.extend(files_)
#     print('v2')
else:
    files_lcd_input.extend(file_last_modified)


# In[48]:


# string version of filenames from files_lcd_input as vertical list
files_lcd_input_names_str = "\n".join([f_.name for f_ in files_lcd_input])
# files_lcd_input_names_str


# #### Which columns are present by file in files_lcd_input?

# In[49]:


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


# ### Create files_usecols containing validated files
# and columns to be used
# _validation for each file:_
# * is their a 'DATE' column?
# * is at least one of the `cols_data` columns available?
# * keep only columns found in `cols_noaa_processed`

# #### Is 'DATE' available for every file in files_lcd_input?

# In[50]:


# keep only files that have a 'DATE' column - otherwise where is this data supposed to go?
files_usecols = {file_ : cols_ for file_, cols_ in files_columns.items()
                 if 'DATE' in cols_}


# #### Keep only files that have at least one cols_data column

# In[51]:


files_usecols = {file_ : cols_ for file_, cols_ in files_usecols.items()
                 if len(set(cols_).intersection(set(cols_data))) >=1}


# In[52]:


# reduce files_usecols to only columns used in this process
files_usecols = {file_ : sorted(set(cols_noaa_processed).intersection(set(cols_))) for
                 file_, cols_ in files_usecols.items()}


# ### Create df from files_usecols

# In[127]:


df = pd.concat((pd.read_csv(f_, usecols=cols_, parse_dates=['DATE'],
                            index_col='DATE', low_memory=False) for
                f_, cols_ in files_usecols.items()), axis=0)\
                .reset_index().drop_duplicates()
df = df.set_index('DATE', drop=True).sort_index()
df


# In[128]:


# keep track of the count of raw timestamps prior to processing
n_records_raw = df.shape[0]
# track statistics by column prior to processing, omit 'Sunrise' & 'Sunset' from stats
cols_sunrise_sunset = df.columns.intersection(['Sunrise', 'Sunset']).tolist()
df_stats_pre = df.loc[:, df.columns.difference(cols_sunrise_sunset)].describe()


# In[129]:


# df = df[cols_use].copy()
df.shape


# In[130]:


df.head()


# ### Identify and Display Weather Station Information

# In[131]:


# v1 & v2
# identify WBAN station
station_lcd = str(df['STATION'].value_counts().index[0])
station_wban = station_lcd[6:]  #important - this is index for the isd-history table
station_call = station_lcd[-4:] #needed for non-USA locations with 99999 WBAN
station_lcd, station_wban


# In[132]:


# remove 'STATION', 'REPORT_TYPE', 'SOURCE' columns - not needed anymore
df.drop(columns=['STATION', 'REPORT_TYPE', 'SOURCE'],
        inplace=True, errors='ignore')


# #### Open 'isd-history.csv' containing Station details
# This is location identification information.  source:  https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt.  Parsed by 'ISD History Station Table.py'.

# In[133]:


isd_history_available = False
file_isd_history = find_latest_file(dir_data, pattern_isd_history_file)
if file_isd_history.is_file():
    isd_history_available = True


# #### Create df_isd_history for Station Detail lookup

# In[134]:


df_isd_history = pd.read_csv(file_isd_history, index_col='WBAN',
                     dtype={'WBAN': object}).sort_values(
                    by=['USAF', 'BEGIN'], ascending=[True, False])
df_isd_history.sample(5).sort_index()


# In[135]:


df_isd_history.info()


# In[136]:


df_isd_history.loc[df_isd_history['CALL']==station_call]


# In[137]:


# is the station WBAN listed in df_isd_history?
station_details_available_wban = station_wban in df_isd_history.index


# In[138]:


# is the station CALL listed in df_isd_history?
station_details_available_call = station_call in df_isd_history['CALL'].values


# In[139]:


any([station_details_available_wban, station_details_available_call])


# In[140]:


if station_details_available_wban:
    station_details = dict(df_isd_history.loc[station_wban].reset_index()\
                       .sort_values('END', ascending=False).iloc[0])
elif station_details_available_call:
    station_details = dict(df_isd_history.loc[
                        df_isd_history['CALL'] == station_call]\
                       .reset_index().sort_values('END',
                          ascending=False).iloc[0])
else:
    station_details = {col_ : 'Unknown' for col_ in df_isd_history.columns}


# In[141]:


if station_details['LAT'] != 'Unknown':
     # add url to google maps search of lat, lon values to station_details
    google_maps_lat_lon_url = """https://maps.google.com/?q={lat},{long}"""
    google_maps_url = google_maps_lat_lon_url.format(lat = station_details['LAT'],
                                                    long = station_details['LON'])
    station_details['GOOGLE MAP'] = google_maps_url

# delete df_isd_history - no longer needed
del df_isd_history


# In[142]:


station_details


# In[143]:


#     create timestamps for consolidated table df
start_dt = df.index[0]
end_dt = df.index[-1]
start_str = start_dt.strftime('%Y-%m-%d')
end_str = end_dt.strftime('%Y-%m-%d')
start_str, end_str


# In[144]:


# identify hourly timestamps where the LCD source reported no observations
# This will be added as a boolean column later
idx_hours_no_source_data = pd.date_range(start_dt, end_dt, freq='H')\
                            .difference(df.index.round('H'))
# how many hours of the curent time range have no observations?
n_hours_no_source_data = len(idx_hours_no_source_data)
# idx_hours_no_source_data


# In[145]:


for col_ in df.columns:
    df[col_] = pd.to_numeric(df[col_], errors='coerce')
    try:
        df[col_] = df[col_].astype(float)
    except:
        pass


# #### Resolve duplicate datetime index values

# In[148]:


# if a single timestamp appears more than once, average available values
# to return a single value and single timestamp (ignoring 
# NaN values of course)
df = df.groupby(level=0).mean()
df.shape


# #### Extract Sunrise and Sunset by date in to dictionaries
# 
# to be applied to df_out towards end of script.
# Drop Sunrise and Sunset columns after extraction here.
# The source data provides only one unique sunrise/set value per day and
# the rest of the day's values are NaN

# In[149]:


# create date_sunrise/sunset dictionaries with dates as keys and 
# timestamp values for time to be added back in to resampled df
date_sunrise = datetime_from_HHMM(df['Sunrise'].dropna()).to_dict()
date_sunset = datetime_from_HHMM(df['Sunset'].dropna()).to_dict()


# In[97]:


# drop sunrise/sunset columns as their information is now 
# contained in the date_sunrise/sunset dictionaries
df.drop(columns=cols_sunrise_sunset, inplace=True, errors='ignore')


# #### are there timestamps that have a high count of null values?
# In v1 LCD files the '23:59:00' timestamp is suspect and appears to only be a placeholder
# for posting sunrise/sunset times.  Important that this step be done after
# forward filling sunrise/sunset values. 
# V2 LCD files do not seem to have the '23:59:00' timestamp issue.

# In[98]:


# n_records_hourly_approx = int(df.shape[0]/(24))
# n_max_null = pct_null_timestamp_max * n_records_hourly_approx
n_max_null = int(pct_null_timestamp_max * df.shape[0])
n_max_null


# In[99]:


temp = df.loc[:, df.columns.difference(cols_sunrise_sunset)]
df_nan_ts = temp.groupby(temp.index.time).apply(lambda x: x.isna().sum()\
                            .gt(n_max_null)).all(axis=1)
times_nan = df_nan_ts.loc[df_nan_ts].index.tolist()
del temp
del df_nan_ts


# In[100]:


# remove records for timestamps with a high percentage of Null values.
# note that the '23:59:00' timestamp is suspect and appears to only be a placeholder
# for posting sunrise/sunset times.  Important that this step be done after
# forward filling sunrise/sunset values.
filter_nan_times = pd.Series(df.index.time).isin(times_nan).values
df = df.loc[~filter_nan_times]
df.info()


# In[101]:


# test = df.between_time('23:01:00', '00:59:00').select_dtypes(include=[int, float])
# test.groupby(test.index.time).sum()


# In[102]:


if is_development:
    df.groupby(df.index.time).count().max(axis=1).sort_index().plot(figsize=(11,3),
   title='Count of Maximum Non-Null Readings per "time" Timestamp')


# In[103]:


# df.loc[filter_nan_times]


# In[104]:


#     Check what percentage of data has null data and print to screen
df_pct_null_data = pd.DataFrame({'Percent N/A': df.isnull().sum().divide(len(df)).round(3)})
df_pct_null_data_pre_formatted = df_pct_null_data['Percent N/A']\
                            .apply(lambda n: '{:,.1%}'.format(n))
# remove 'Hourly' prefix for display only
col_rename_remove_hourly = {col_ : col_.replace('Hourly', '') for
                            col_ in df_pct_null_data_pre_formatted.index}


# #### Display Station Details

# In[105]:


# exclude station lifetime history dates - could cause confusion
station_details_exclude = ['BEGIN', 'END']
station_details_display = {k_ : v_ for k_, v_ in station_details.items() if
                           k_ not in station_details_exclude}


# In[107]:


print('--------------------------------------------')
print('------ ISD Weather Station Properties ------')
print('--------------------------------------------')
for k_, v_ in station_details_display.items():
    print("{:<15} {:<10}".format(k_, v_))
print('\n')


# In[108]:


# message_pct_null_data = f"""Percent Missing Values by Column for LCD source file '{file_lcd_input.name}' for USAF station {station_usaf} at '{station_details['STATION NAME']}' from {start_str} to {end_str}."""
# message_pct_null_data = """Percent Missing Values by Column for LCD source file(s):
# {files_lcd_input_names_str}\n\nFor USAF station {station_usaf} at '{station_name}'
# from {start_str} to {end_str}."""
message_pct_null_data = """Percent Missing Values by Column from {start_str} to {end_str} for LCD source file(s):\n
{files_lcd_input_names_str}"""
message_ = message_pct_null_data.format(files_lcd_input_names_str = files_lcd_input_names_str,
                            station_usaf = station_details['USAF'],
                            station_name = station_details['STATION NAME'],
                            start_str = start_str,
                            end_str = end_str)

print(message_)


# In[109]:


print('--------------------------------------------------------------')
print('------ Percent Null Values by Column Before Processing -------')
print('--------------------------------------------------------------')
display(df_pct_null_data_pre_formatted.rename(index=col_rename_remove_hourly))


# ### Resample Hourly

# In[110]:


get_ipython().run_cell_magic('time', '', "dfs = {}\n# individually resample each column on an hourly frequency.\n# This will produce series\n# with perfect, complete datetime indexes.  However, it is quite\n# possible that NaN values will remain (ie. a contiguous 3-hour\n# period of NaN values).  Remaining NaN values will\n# be resolved through interpolation later in the script.\n# this method is used because NaN values can appear at different timestamps\n# in each column\n# at this point the df should contain only numeric data\nfor col_ in df.columns:\n    print(col_)\n    dfs[col_] = df[col_].dropna().resample('H').mean()\n")


# ### Create df_out - the beginning of the final output

# In[111]:


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
df_out


# ### Interpolate Null Values
# According to the following parameters:
# Because observed weather data commonly contains gaps (ie., NaN or null values), noaa-weather-hourly will attempt to fill in any such gaps to ensure that in each record a value is present for all of the hourly timestamps. To do so, it will use time-based interpolation for gaps up to a default value of 24 hours long ('max_records_to_interpolate').  For example if the dry bulb temperature has a gap with neighboring observed values like (20, X, X, X, X, 25), noaa-weather-hourly will replace the missing values to give (20, 21, 22, 23, 24, 25).
# 
# If a gap exists in the data that is larger than max_records_to_interpolate, NaN values will be left untouched and a complete datetime index will be preserved.

# In[112]:


df_out = df_out.interpolate(method='time',
            limit = max_records_to_interpolate)


# ### Optional Frequency Resample
# If the freqstr is not 'H', resample.  If the input freqstr is higher than 'H', resample and interpolate, else resample using mean.

# In[113]:


# freqstr = '30T'


# In[114]:


run_resample = False
resample_interpolate = False
#     what is the delta value of the input freqstr?
freqstr_delta = pd.date_range(start_dt, periods=100,
                           freq=freqstr).freq.delta
# If the freqstr is not 'H', run the resample process
if freqstr != 'H':
    run_resample = True

# If the input freqstr is higher frequency 
# than df_out, resample using interpolation
resample_interpolate = freqstr_delta < df_out.index.freq.delta


# In[115]:


if run_resample:
#     resample via interpolation
    if resample_interpolate:
        df_out = df_out.resample(freqstr).interpolate()
# or resample using mean
    elif not resample_interpolate:
        df_out = df_out.resample(freqstr).mean()


# In[116]:


df_out.info()


# ### Pre- Post-Processing Statistical Comparison

# In[117]:


# create general statistics on post-processed dataset for
# comparison with pre-processed dataset to understand how/if 
# processing significantly altered series values
df_stats_post = df_out[df_stats_pre.columns].describe()
df_stats_post


# In[118]:


df_mean_comp = pd.concat([df_stats_pre.loc['mean'].T, df_stats_post.loc['mean'].T],
                         axis=1, keys=['Source Mean', 'Processed Mean']).round(2)
df_mean_comp['% Difference'] = df_mean_comp.pct_change(axis=1).iloc[:,-1]\
                                .fillna(0).round(3)\
                                .apply(lambda n: '{:,.1%}'.format(n))
df_mean_comp


# In[119]:


# TO-DO:  Overall pre- post- statistics check
df_stats_pre.sub(df_stats_post).div(df_stats_pre).mean().mean()
# df_stats_pre.pct_change(df_stats_post)
# df_stats_pre.eq(df_stats_post).sum().sum()
# df_stats_pre.size


# In[120]:


#     Check what percentage of data has null data and print to screen
df_pct_null_data_post = pd.DataFrame({'Percent N/A': df_out.isnull()\
                              .sum().divide(len(df_out)).round(4)})
df_pct_null_data_post_formatted = df_pct_null_data_post['Percent N/A']\
                                .apply(lambda n: '{:,.2%}'.format(n))
display(df_pct_null_data_post_formatted.rename(
                index = col_rename_remove_hourly))


# In[121]:


df_pct_null_comp = pd.concat([df_pct_null_data_pre_formatted, 
                             df_pct_null_data_post_formatted], 
                            axis=1).rename(index=col_rename_remove_hourly)
df_pct_null_comp


# In[122]:


# Round df_out to 1 decimal place
df_out = df_out.round(1)


# ### Add Sunrise/Sunset timestamps to df_out

# In[124]:


pd.DataFrame.from_dict(date_sunrise, orient='index')\
                    .reindex(df_out.index).ffill().astype('datetime64[s]')


# In[151]:


# apply date_sunrise/sunset to df_out index to create sunrise/sunset columns
for col_, dict_ in zip(cols_sunrise_sunset, [date_sunrise, date_sunset]):
    if len(dict_) > 1:
        df_out[col_] = pd.DataFrame.from_dict(dict_, orient='index')\
                    .reindex(df_out.index).ffill().astype('datetime64[s]')
    else:
        df_out[col_] = pd.NaT


# In[152]:


if is_development:
#     df_out[cols_sunrise_sunset].diff(axis=1).iloc[:,-1].dt.total_seconds().div(3600).plot()
    df_out[cols_sunrise_sunset].diff(axis=1).iloc[:,-1]\
        .dt.seconds.div(3600).plot(
        title = 'Duration of Daylight (hours)', figsize = (11,3), lw=3)


# In[153]:


# add column to document hourly obervations where no source data was provided.
df_out['No source data'] = df_out.index.isin(idx_hours_no_source_data)


# ### Quality Control

# #### No duplicate records

# #### Complete and consistent timestamps

# #### correct dtypes

# #### Nan values only in columns permitted to have NaN

# #### Rename Columns - remove 'hourly' from names

# In[154]:


df_out.rename(columns=col_rename_remove_hourly, errors='ignore',
             inplace=True)


# ### Save Outputs to Disk
# * df_out
# * df_mean_comp
# * df_pct_null_comp

# #### TO-DO:
# Consolidated processing summary report as .txt file containing df_mean_comp, df_pct_null_comp, station_details, and other statistics

# #### Name export file 

# In[155]:


# Save output file to current working directory (ie,
# where command line command was entered)
file_out = dir_cwd / file_output_format.format(
            STATION_NAME = station_details['STATION NAME'],
            start_str = start_str,
            end_str = end_str,
            freqstr = freqstr)
# what if file name is too long for current OS? - TO-DO
# file_out.as_posix().__len__()
file_out


# #### Save df_out to csv as file_out

# In[156]:


df_out.to_csv(file_out)
assert file_out.is_file()


# ### Cleanup

# In[157]:


del df_out


# # END
