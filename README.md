# noaa-weather-hourly

`noaa-weather-hourly` cleans historical LCD weather files from the National Oceanic and Atmospheric Administration (NOAA).  It uses a simple command line interface to generate observed hourly (and other frequency) .CSV files.  

## Output Columns:
* Date
* AltimeterSetting
* DewPointTemperature
* DryBulbTemperature
* Precipitation
* PressureChange
* RelativeHumidity
* StationPressure
* Sunrise
* Sunset
* Visibility
* WetBulbTemperature
* WindDirection
* WindGustSpeed
* WindSpeed

## Installation
This is a Python script that requires a local Python installation.  The following method uses pipx for installation which makes the 'noaa-weather-hourly' command available to run from any directory on the computer.

1. __Obtain Code__ through git OR download<BR>
    a. `git clone https://github.com/emskiphoto/noaa-weather-hourly.git` at a terminal prompt (requires git installation [git installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
    a. Simple download….<BR>
    
2. [__Install Python__ (version 3.8 or newer)](https://www.python.org/downloads/#:~:text=Looking%20for%20a%20specific%20release%3F)
3. __Install pipx__ <BR>
    Windows:  
    `py -m pip install --user pipx`<BR>
    `py -m pipx ensurepath`<BR>
    Unix/macOS:<BR>
    `python3 -m pip install --user pipx`<BR>
    `python3 -m pipx ensurepath`<BR>
4. __Install noaa-weather-hourly 
    `pipx install noaa-weather-hourly`

## Usage
Open a terminal prompt ('Powershell' in Windows) and process the sample LCD file ".\data\test_file_lcd.csv" that is included in installation.  <BR>
$ `noaa-weather-hourly ".\data\test_file_lcd.csv"`

### Usage for Frequencies other than Hourly
The default output contains Hourly frequency data.  Any of the following data frequencies can be output using the `-frequency` argument:<BR>
$ `noaa-weather-hourly [-frequency FREQUENCY] filename`

For example, a 15-minute frequency output:<BR>
$ `noaa-weather-hourly -frequency '15T' '<path_to_LCD_CSV_file>'`

Or a daily frequency output:<BR>
$ `noaa-weather-hourly -frequency 'D' '<path_to_LCD_CSV_file>'`

'D': 'Daily',
'W': 'Weekly',
'M': 'Monthly',
'Q': 'Quarterly',
'Y': 'Yearly',
'H': 'Hourly',
'T': 'Minutely'


## Download NOAA LCD .CSV file
`noaa-weather-hourly` takes a raw NOAA Local Climatological Data .csv-format file as input.   Download file(s) for a specific location and date range from NOAA as follows.  NOAA changed the download process & interface in 2024 to use AWS buckets for storage.  As of December 2024 the new and old methods both work. 

[NOAA Data Tools: Local Climatological Data](https://www.ncdc.noaa.gov/cdo-web/datatools/lcd)
[LCD Documentation](https://www.ncei.noaa.gov/data/local-climatological-data/doc/LCD_documentation.pdf)

It is recommended to store downloaded files in separate folders by location.   

### Before Spring 2024 (_multiple years in a single, large file_):
[<img alt="NOAA LCD Website" width="800px" src="images\NOAA_LCD_data_tools_website.PNG" />]
1. Go to [NOAA Data Tools: Local Climatological Data](https://www.ncdc.noaa.gov/cdo-web/datatools/lcd)
2. Find the desired Weather Station and select 'Add to Cart'
3. Click on 'cart (Free items)'
4. Select the Output Format 'LCD CSV'
5. Select the Date Range.  Consider adding an additional week before and after the needed date range to support interpolation of missing values.
6. "Enter Email Address" where a link to the LCD CSV download should be delivered.
7. "Submit Order"
8. Check email inbox for a "Climate Data Online request 1234567 complete" message and Download the LCD CSV file to a local folder using the "Download" link.

### After Spring 2024 (_one or more files per calendar year, or single multi-year bundle_):
[<img alt="NOAA LCD2 Website" width="600px" src="images\NOAA_LCD2_data_tools_website.PNG" />]
1. Go to [Local Climatological Data (LCD), Version 2 (LCDv2)](https://www.ncei.noaa.gov/access/search/data-search/local-climatological-data-v2)
2. __What ?__: Select columns to be included in the file by clicking on 'Show List'.    
    - Beware that selecting columns that are not available for a given location will result in that location being excluded entirely from the search results.  
    - It's recommended to select only the columns listed in  [Output Columns](#output-columns:)  
3. __Where ?__:  Input weather station location.  A list of all available annual weather files for all matching locations will be displayed.  Use the 'When' inputs to filter this list.
4. __When ?__:  (optional) For a single calendar year, select any date in that year.  For multiple calendar years click 'Select Date Range' and input start and end dates of the range.
5. (Recommended) Review list of matching files and click "Download" for each file.
    - (Alternatively) Merge multiple years of data as a single large file by "+ Select" multiple files.  Then select "Output Format" csv, click on "Configure and Add" and "Add Order to Cart".  "Proceed to Cart", provide and Email address and click "Submit".  Check email inbox for a "Climate Data Online request 1234567 complete" message and download the LCD CSV file to any local folder using the "Download" link.  

## Process Details
The `noaa-weather-hourly` makes the source LCD file ready-to-use by resolving the following data formatting and quality issues.  
[<img alt="Raw LCD file data issues" width="600px" src='images\Raw LCD file data issues.PNG' />] 
    
There are more than 100 possible source columns, but `noaa-weather-hourly` processes only 'Hourly...' columns and 'Sunrise', 'Sunset' & 'DATE' columns.  This is a standalone process that does not access any external (internet) resources and operates only in the directory it is intiated in.

1. Creates a copy of the source LCD file(s), leaving the source file(s) unmodified
2. Extracts ID data and gathers additional station details
3. Merges multiple source files having the same station ID and resolves overlapping date ranges
4. Formats 'Sunrise' and 'Sunset' times
5. Removes recurring daily timestamps that contain more null values than allowed by 'pct_null_timestamp_max' parameter
6. Displays the percent of null values in source data to screen
7. Resamples and/or interpolates values per the input '-frequency' value
    - most columns are expected to have non-null values for every timestamp (i.e., 'DryBulbTemperature')
    - some columns are expected to have null values at some times and the null values are preserved in the output (ie., 'Precipitation', 'WindGustSpeed') 
8. Saves a single .CSV file to the same location as the source LCD file(s) (will overwrite existing files if an identical file already exists).
9. Output file is named "{STATION_NAME} {from_str} to {end_str} {freqstr}.csv", (ie.,
    "CHICAGO O'HARE INTERNATIONAL 2020-01-01 to 2023-12-31_H.csv")

### Weather Station Directory
`noaa-weather-hourly` includes a processed 'isd-history.csv' file containing the details of ~4300 active stations and ID cross-references (ICAO, FAA, WMO, WBAN) provided by [Historical Observing Metadata Repository (HOMR)](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt).  This data is only used to define LCD weather file location data as this is not provided in the LCD CSV itself.  The data source is updated regularly, but the version in this script is not.  If updates are needed, consider running the 'ISD History Station Table.py' to update 'data/isd-history.csv'.

### Limitations:
* NOAA LCD source is for atmospheric data primarily for locations in the United States of America.
* NOAA LCD data is not certified for use in litigation
* `noaa-weather-hourly` is not an API
* `noaa-weather-hourly` Python module does not (currently) integrate with other Python tools
* Does not validate
* Does not visualize
* Processes only 'Hourly...' columns and 'Sunrise', 'Sunset' & 'DATE'
* Does not modify values from source
    - Does not filter or smooth apparently noisy source data
* Does not process or convert categorical data like 'HourlySkyConditions'
* Does not compare to other references
* No Forecast

    
## Acknowledgements
* [diyepw](https://github.com/IMMM-SFA/diyepw/tree/main) -  Amanda D. Smith, Benjamin Stürmer, Travis Thurber, & Chris R. Vernon. (2021). diyepw: A Python package for [EnergyPlus Weather (EPW) files](https://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html) generation. Zenodo. https://doi.org/10.5281/zenodo.5258122<BR>
* [pycli](https://github.com/trstringer/pycli/tree/master) - Python command-line interface reference
* [Degree Days.net](https://www.degreedays.net/) - Excellent reference for weather-related energy engineering analysis    

## Example Alternative Observed Weather Data Sources
http://weather.whiteboxtechnologies.com/hist<BR>
https://openweathermap.org/history<BR>
https://docs.synopticdata.com/services/weather-data-api<BR>
https://mesowest.utah.edu/<BR>
https://registry.opendata.aws/noaa-isd/<BR>
https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database<BR>
https://registry.opendata.aws/noaa-isd/<BR>

## Related Weather & Energy Model Code
https://github.com/celikfatih/noaa-weather<BR>
https://github.com/cagledw/climate_analyzer<BR>
https://pypi.org/project/diyepw/<BR>
https://github.com/GClunies/noaa_coops<BR>
https://github.com/DevinRShaw/simple_noaa<BR>
https://github.com/awslabs/amazon-asdi/tree/main/examples/noaa-isd<BR>
https://pypi.org/project/climate-analyzer<BR>



## TL;DR - Background
### Different Weather Causes Different Performance
Weather-dependent models like building energy models generally use typical weather values to estimate a given metric for a system.  For example, typical weather values would be used to estimate the annual energy consumption of a building cooling system.  Inevitably, the actual weather the system experiences in the real world is _different_ than the weather used to create the model.  If the model is sensitive to weather the distinct typical & actual weather values will cause cumulative metrics to be different.  If the amplitude of these differences is larger than the cumulative impact of individual system elements (ex. the cooling system), it may not be possible to compare modeled and actual performance.  

### Analysis by Spreadsheet
The use cases below often require reporting & analysis that is easy to access, distribute, understand and review.  Therefore, energy engineers often must use spreadsheet software like MS Excel, Google Sheets, etc.  `noaa-weather-hourly` is developed for to support spreadsheet analysis.  

### Financial Context of Energy Models
Many building design choices must be made before a physical building exists, and once equipment is installed, changing design choices become costly.  The installed performance will likely persist as-is for a decade or more until equipment needs to be replaced.   The building owners and the environment will feel the impact of early-stage design choices every year until equipment is changed.  Because the life-cycle cost of _operating_ the equipment may be several times larger than the _initial purchase price_, it is cost-effective to develop energy models that optimize operational cost and inform system design choices.

### Measurement & Verification of Modeled Expectations
Incentives and financing of high-efficiency solutions are ubiquitous.  When large financial incentives are in play, many providers must measure and verify (M&V) the true impact of specific system elements (energy conservation measures) to ensure that incentives are returning the intended results.   

Energy Service Companies (ESCO) and other efficiency solutions providers often guarantee specific performance improvements in contracts (ie., 10% reduction in annual electricity cost due to cooling system replacement).  If the solution does not achieve the estimated savings, the ESCO is liable for the financial difference in operating cost and possibly more.  Observed performance improvements are determined by comparing a baseline model to observed performance.  

In both cases, __the estimation of performance improvements is only valid if the impact of weather variance between model/baseline and observed reality is accounted for__. 

### Solution:  Weather-normalization
The solution to aligning the results of a model made with one set of weather values and actual results resulting from a different set of values is to weather-normalize the results.  This normalization process is only possible if both the typical and actual weather values are available.  Once the modeled and actual results are aligned (ie. the influence of weather variance is removed) the difference in expected and actual performance can be evaluated in detail.

### Availability of Free Weather Data
Weather data is abundant & free in the modern connected world.  However, obtaining good, _usable_ data that is already available in the public forum is not necessarily easy or free of cost.  `noaa-weather-hourly` was created to facilitate convenient, free access to small volumes of hourly USA weather as a convenient .CSV file.  

There are numerous subscription or purchase-based [sources of historical weather]('#example-alternative-observed-weather-data-sources'), and many offer API access.  These sources may be the most cost-effective solution when many locations are needed and/or the data need to be updated frequently.

