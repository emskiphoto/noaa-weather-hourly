# config.py
# noaa-weather-hourly

# command line arguments
filename = ''
freqstr = 'H'

# v1 LCD csv file name regex
pattern_lcd1_input_file = r'^[0-9]{5,10}.csv'
pattern_lcd1_example = '3876540.csv'
# v2 LCD csv file name regex
pattern_lcd2_input_file = r'^LCD_(.*)_[0-9]{4}.csv'
pattern_lcd2_example = 'LCD_USW00014939_2023.csv'
# collect patterns and examples in lists
patterns_lcd_input_files = [pattern_lcd1_input_file, pattern_lcd2_input_file]
patterns_lcd_examples = [pattern_lcd1_example, pattern_lcd2_example]
patterns_lcd_examples_str = " or ".join(patterns_lcd_examples)
# store patterns by version number in dictionary
version_pattern_lcd_input = {idx_ : v_ for idx_, v_ in enumerate(patterns_lcd_input_files, start=1)}

# file naming conventions
pattern_isd_history_file = r'isd-history.csv|ISD-HISTORY.CSV'
file_output_format = """{STATION_NAME} {start_str} to {end_str} {freqstr}.csv"""

# Parameters
pct_null_timestamp_max = 0.5
max_records_to_interpolate = 24

freqstr_frequency = {'D': 'Daily',
'W': 'Weekly',
'M': 'Monthly',
'Q': 'Quarterly',
'Y': 'Yearly',
'H': 'Hourly',
'T': 'Minutely',
'MS': 'Month Start',
'ME': 'Month End',
'QS': 'Quarter Start',
'QE': 'Quarter End',
'B': 'Business Day'}

# NOAA columns processed by this script
cols_noaa_processed = ['DATE', 'STATION', 
       'HourlyVisibility', 'HourlyDryBulbTemperature', 'HourlyWindSpeed',
       'HourlyDewPointTemperature', 'HourlyRelativeHumidity',
       'HourlyWindDirection', 'HourlyStationPressure',
       'HourlyWetBulbTemperature',
       'HourlyAltimeterSetting',
       'HourlyPrecipitation', 'HourlyPressureChange',
        'HourlyWindGustSpeed', 'Sunset',
       'Sunrise']
# need a list of columns with data that excludes 'DATE' and 'STATION'
cols_date_station = ['DATE', 'STATION']
cols_data = [col_ for col_ in cols_noaa_processed if col_ not in cols_date_station]

# Messages
message_all_csv_files_found = """The following .CSV files were found in '{dir_source_posix}':
{dir_csv_files_str}\n"""

message_no_csv_files_found = """***  PROCESS ABORTED  ***\n\nNo .CSV-format files found in:
'{dir_source_posix}'\n
noaa-weather-hourly must be executed in a directory that contains original LCD-format file(s)
from NOAA.  Copy NOAA files to the current directory or
execute noaa-weather-hourly in a directory that contains NOAA LCD CSV files.

NOAA LCD files can be obtained from the following sources:
- https://www.ncdc.noaa.gov/cdo-web/datatools/lcd
- https://www.ncei.noaa.gov/access/search/data-search/local-climatological-data-v2

For further detail, refer to:
https://github.com/emskiphoto/noaa-weather-hourly
"""

message_no_lcd_files_found = """***  PROCESS ABORTED  ***\n\nNo LCD-format file names found in:
'{dir_source_posix}'\n
noaa-weather-hourly must be executed in a directory that contains original LCD-format file(s)
from NOAA whose name(s) have not been changed.  Copy NOAA files to the current directory or
execute noaa-weather-hourly in a directory that contains NOAA files.
\nExample LCD file names:\n'{patterns_lcd_examples_str}'
\nFiles in current directory:
{dir_csv_files_str}

NOAA LCD files can be obtained from the following sources:
- https://www.ncdc.noaa.gov/cdo-web/datatools/lcd
- https://www.ncei.noaa.gov/access/search/data-search/local-climatological-data-v2

For further detail, refer to:
https://github.com/emskiphoto/noaa-weather-hourly"""
