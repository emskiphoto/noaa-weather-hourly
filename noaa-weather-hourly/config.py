# config.py
# noaa-weather-hourly
freqstr = 'H'
# v1 LCD csv file name regex
pattern_lcd1_input_file = r'^[0-9]{5,10}.csv'
# v2 LCD csv file name regex
pattern_lcd2_input_file = r'^LCD_(.*)_[0-9]{4}.csv'
patterns_lcd_input_files = [pattern_lcd1_input_file, pattern_lcd2_input_file]
version_pattern_lcd_input = {idx_ : v_ for idx_, v_ in enumerate(patterns_lcd_input_files, start=1)}
pattern_isd_history_file = r'isd-history.csv|ISD-HISTORY.CSV'
file_output_format = """{STATION_NAME} {from_str} to {end_str} {freqstr}.csv"""
pct_null_timestamp_max = 0.5

freqstr_frequency = {'D': 'Daily',
'W': 'Weekly',
'M': 'Monthly',
'Q': 'Quarterly',
'Y': 'Yearly',
'H': 'Hourly',
'T': 'Minutely',
'S': 'Secondly',
'MS': 'Month Start',
'ME': 'Month End',
'QS': 'Quarter Start',
'QE': 'Quarter End',
'B': 'Business Day'}
