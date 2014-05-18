#!/usr/bin/env python

import serial
import time
import datetime
import os
import sys
import getopt
import string
import urllib
import re
from metar import Metar
from netifaces import ifaddresses
 
def get_metar(_url):
    _obs_dict = 'Invalid ICAO Code'
    try:
        _urlh = urllib.urlopen(_url)
        for _metar in _urlh:
            if _metar.startswith(station):
                _obs = my_metar(_metar, utcdelta=datetime.timedelta(hours=5))
                _obs_dict = _obs.metar_dict()
        if not _metar:
            _obs_dict = 'No Data for ICAO'
    except:
        _obs_dict = 'Could Not Parse METAR'
    return _obs_dict
 
 
class my_metar(Metar.Metar):
 
    def metar_dict( self ):
        _dict = {
            'station': 		      self.station_id,
            'type':  		      self.report_type(),
            'time':                   (self.time - self._utcdelta).strftime('%I:%M %p'),
            'temperature':            self.temp.string('F'),
            'dew point':              self.dewpt.string('F'),
            'wind':                   self.wind('MPH'),
            'peak wind':              self.peak_wind('MPH'),
            'wind shift':             self.wind_shift(),
            'visibility':             self.visibility(),
            'visual range':           self.runway_visual_range(),
            'pressure':               self.press.string(),
            'weather':                self.present_weather(),
            'sky':                    self.sky_conditions('\n     '),
            '6-hour max temp':        str(self.max_temp_6hr),
            '6-hour min temp':        str(self.min_temp_6hr),
            '24-hour max temp':       str(self.max_temp_24hr),
            '24-hour min temp':       str(self.min_temp_24hr),
            '1-hour precipitation':   str(self.precip_1hr),
            '3-hour precipitation':   str(self.precip_3hr),
            '6-hour precipitation':   str(self.precip_6hr),
            '24-hour precipitation':  str(self.precip_24hr)
        }
        return _dict
        
# Constants for the Noritake CU-Y Series VFD
esc            = '\x1b'
esc_initialize = esc+'\x40'
esc_blink      = esc+'\x42'
esc_no_blink   = esc+'\x41'
no_cursor      = '\x14'
clear_home     = '\x0c'
crlf           = '\r\n'
brightness     = '\x1f\x58\x01'

# Constants for the METAR part
station        = 'KLWC'
BASE_URL       = 'http://weather.noaa.gov/pub/data/observations/metar/stations'
url            = '%s/%s.TXT' % (BASE_URL, station)
debug          = False

# Start up serial port and initialize the display
uart = serial.Serial("/dev/ttyAMA0", baudrate=38400, timeout=3.0)
uart.write(esc_initialize)
uart.write(brightness)
uart.write(no_cursor)
uart.write(clear_home)

update_time = 0

my_ip_address = ifaddresses('wlan0')[2][0]['addr']
uart.write('My IP Address:' + crlf + '    '  + my_ip_address)
time.sleep(1)

while True:
    if time.time() > update_time + 60:
        update_time = time.time()
        obs_dict = get_metar(url)
        
	uart.write(clear_home)
	time.sleep(0)	

        uart.write(clear_home)
        uart.write( station + '  ' + time.strftime('%b %d %I:%M %p') + crlf)
        
        if type(obs_dict) is dict:
            if obs_dict['wind'].find(',') != -1:
                wind_comp = obs_dict['wind'].split(',')
                gust = re.findall('\d+', wind_comp[1])
                wind = wind_comp[0][:-4] + ' gust ' + str(gust[0])
            else:
                wind = obs_dict['wind']
            uart.write(' Valid: ' + obs_dict['time'] + crlf)
            uart.write(' Temp: ' + obs_dict['temperature'][:-4] + '\xf8' + crlf)
            uart.write(' Wind: ' + wind)
        else:
            uart.write(obs_dict)
      	time.sleep(60)
