#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup(name = 'noaa_weather_hourly',
    version = '0.1.0',
    packages = ['noaa_weather_hourly'],
    entry_points = {
        'console_scripts': [
            'noaa_weather_hourly = noaa_weather_hourly.__main__:__main__'
        ]
    })