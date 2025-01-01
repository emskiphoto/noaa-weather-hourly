# utils.py
# noaa-weather-hourly
import pathlib
import re

def say_hello():
    print('Hello from the Utils.py module')
    
def find_latest_file(directory, pattern):
    """Returns pathlib file path object for most recently modified file in 'directory' whose
    path/name matches 'pattern'.  The 'pattern' is the same pattern that would be input in the
    pathlib.glob() function.  
    Example Usage:  path = find_latest_file(pathlib.Path('data'), '*Minnesota.csv')"""
    try:
        return sorted([(f, f.stat().st_mtime) for f in directory.glob('*') 
                       if re.match(pattern, f.name)],
           key=lambda x: x[1], reverse=True)[0][0]
    except:
        return None
    
def find_file_re_pattern(directory, pattern):
    """Returns list of file names (name only, not paths) in the
    input Pathlib 'directory' that match
    the regular expression 'pattern' provided"""
    try:
        return [x for x in directory.glob('*') if
                          re.search(pattern, x.name) != None]
    except:
        return None
    
    
def find_files_re_pattern_sorted_last_modified(directory, pattern, descending=True):
    """Returns list of pathlib file path objects for most recently modified file
    in 'directory' whose path/name matches 'pattern'.  The 'pattern' is the same pattern
    that would be input in the pathlib.glob() function.  
    Example Usage:  paths = find_file_re_pattern_sorted_last_modified(
                    pathlib.Path('data'), '*Minnesota.csv')"""
    try:
        return [x_[0] for x_ in sorted([(f, f.stat().st_mtime) for f in 
                         find_file_re_pattern(directory, pattern)],
                           key=lambda x: x[1], reverse=descending)]
    except:
        return None