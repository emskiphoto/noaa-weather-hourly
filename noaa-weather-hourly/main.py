# noaa-weather-hourly
# this is a CLI script intended to test basic functionality
# it reads a local CSV and writes a modified version back to disk with a new name
# script can take in multiple command line arguments


import argparse
from pandas import read_csv
from utils import *
from config import *

parser = argparse.ArgumentParser(description='Open a CSV file.')
# required argument 'filename'
parser.add_argument('filename', help='The CSV file to open')
# To make an argument optional in argparse, you simply need to add a prefix to the argument name, typically either a single hyphen (-) or a double hyphen (--)
parser.add_argument('-frequency', type=str, help='Frequency of output data')

args = parser.parse_args()

# def say_hello():
#     print('Hello')

if __name__ == '__main__':
    print(args.filename)
    print(args.frequency)
#     at this point the args.frequency variable doesn't actually do anything - just print it for now
    if args.frequency != None:
        if args.frequency != 'H':
            print(f'Resamplng at "{freqstr_frequency[args.frequency]}" frequency')
    file_in = args.filename
    file_out = file_in.replace('.csv', '_shuffled.csv')
    
    df = read_csv(file_in)
    
    print(df.head())
    print('\nshuffling table order at random\n')
    df = df.sample(df.shape[0])
    print('\n', df.head(), '\n')
    df.to_csv(file_out)
    print(f'\nsaving {file_out} to disk\n')
    say_hello()
    