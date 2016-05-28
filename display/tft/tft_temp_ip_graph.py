#!/usr/bin/env python
#
# Temp Graph
#
__author__ = "James Morris"
__version__ = 0.1

import os
import sys
import sqlite3
import time
from datetime import datetime

import Adafruit_DHT

# Temperature Sensor
ShowTemp = False
sensor = Adafruit_DHT.AM2302
pin = '4'

from libtft import TFTLib

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

class TFTGraphTemp(object):
        
    """ For Displaying text on a 1.8" TFT 128x160 """
    
    _MAX_COLS = 120 # 127
    _MAX_ROWS = 150 # 159

    _MAX_POINTS = 120 

    _ROOM_TEMP  = 78
    _START_TEMP = 70
    _MAX_TEMP   = 90

    _OffsetX = 1 # T-B
    _OffsetY = 1 # L-R

    _FontX = 5
    _FontY = 7

    _ScaleX = 1
    _ScaleY = 4

    _GridX = 10
    _GridY = 10

    _HOURS_PER_DAY = 24

    _ROTATION = 180

    _Coordinate = False
    _Graph = False
    _SHOW_TEMP_LINE = False

    def __init__(self):
        self.libtft = TFTLib()
        self.dbFile = "/home/pi/rpi/Weather/Weather.db"

    def __del__(self):
        pass

    def _getTemperatures(self):
        """ Load Temperatures"""
        
        conn = sqlite3.connect(self.dbFile)

        # ID = row[0]
        # ReadingDateTime = row[1]
        # TempC = row[2]
        # Tempf = row[3]
        # Humidity = row[4]

        ins = "select * from temperature_temperature order by ID desc"
        cursor = conn.execute(ins)

        temps = [[x[0], x[1], x[3]] for x in cursor]

        return temps

    def drawCoordinates(self):
        """ Draw Coordinates to check orientation is correct"""
        
        adjust = 30
        
        self.libtft.DrawRect(adjust, adjust, self._MAX_COLS - adjust, self._MAX_ROWS - adjust, self.libtft.GREEN)
        
        x = adjust - (adjust / 2)
        y = adjust
        st = "%d, %d" % (x, y)
        self.libtft.PutSt(st, x, y)
        self.libtft.DrawPixel(x, y, self.libtft.GREEN)
           
        x = self._MAX_COLS - adjust  - (adjust / 2)
        y = self._MAX_ROWS - adjust
        st = "%d, %d" % (x, y)
        self.libtft.PutSt(st, x, y)
        self.libtft.DrawPixel(x, y, self.libtft.GREEN)
        
        x = adjust - (adjust / 2)
        y = self._MAX_ROWS - adjust
        st = "%d, %d" % (x, y)  
        self.libtft.PutSt(st, x, y)
        self.libtft.DrawPixel(x, y, self.libtft.GREEN)

        x = self._MAX_COLS - adjust - (adjust / 2)
        y = adjust
        st = "%d, %d" % (x, y)  
        self.libtft.PutSt(st, x, y)
        self.libtft.DrawPixel(x, y, self.libtft.GREEN)

    def _plotGrid(self):
        """ Plot a Grid on the screen"""
                
        vx = self._GridX
        while vx < self._MAX_COLS:
            self.libtft.VLine(vx, 1, self._MAX_ROWS - 1, self.libtft.GRAY)
            vx += self._GridX
            
        vy = self._GridY
        while vy < self._MAX_ROWS:
            self.libtft.HLine(1, self._MAX_COLS - 1, vy, self.libtft.GRAY)
            vy += self._GridY
            
    def _parseReading(self, temp):
        """Parse Temperature Reading"""
        
        logger.debug("%s" % temp)
        time = temp[1][8:16]
        
        logger.debug("time - %s" % time)
        hour = int(time[:2])
        minutes = int(time[3:5])
        day = int(temp[1][5:6])
        month = temp[1][0:3]
        
        tfr = round(float(temp[2][:-4]), 0)
        tf = int(tfr)

        if time[6] == "P" and hour != 12:
            logger.debug("---Adjust : %d PM" % hour)
            hour += 12

        if  minutes > 30:
            logger.debug("+++Round : %d" % hour)
            hour += 1

        logger.debug("!!!%2d - %d:%d" % (tf, hour, minutes))

        return tf, month, day, hour, minutes

        
    def plotTemp(self):
        """Draw a series of lines on display"""
        
        # self.libtft.ClearScreen()

        self.libtft.SetOrientation(self._ROTATION)

        temps = self._getTemperatures()
        
        if self._Coordinate:
            drawCoordinates()

        if self._Graph:
            self._plotGrid()

        #
        # Draw Temps
        #
        adjust = 10

        startDay = 0
        
        for temp in temps[:self._MAX_POINTS]:
            tf, month, day, hour, minutes = self._parseReading(temp)

            if startDay == 0:
                
                startDay = day
                x = hour
                
                st = "%s" % (month)
                self.libtft.PutSt(st, 0, self._ROOM_TEMP + (4 * self._FontY), c=self.libtft.WHITE)

                for n in range(0, (self._MAX_COLS / self._HOURS_PER_DAY)):
                    st = "%d" % (startDay - n)
                    x = startDay + (n *  self._HOURS_PER_DAY * self._ScaleX)
                    self.libtft.PutSt(st, x, self._ROOM_TEMP + (2 * self._FontY), c=self.libtft.WHITE)
                
                continue
            
            else:
                x  = ((startDay - day) * self._HOURS_PER_DAY) + hour
                y = self._ROOM_TEMP + ((tf - self._ROOM_TEMP) * self._ScaleY)
            
                logger.debug("%d F _ %02d,%02d" % (tf, x, y))
            
                self.libtft.SetPixel(x, y, color=self.libtft.YELLOW)

        #
        # Draw graph lines
        #
        if self._SHOW_TEMP_LINE:
            y = self._ROOM_TEMP + ((self._MAX_TEMP - self._ROOM_TEMP) * self._ScaleY)
            logger.debug("MAX_TEMP - %d" % y)
            self.libtft.HLine(0, self._MAX_COLS, y, self.libtft.RED) 

        y = self._ROOM_TEMP + ((self._START_TEMP - self._ROOM_TEMP) * self._ScaleY)
        logger.debug("START_TEMP - %d" % y)
        self.libtft.HLine(0, self._MAX_COLS, y, self.libtft.CYAN)

        y = self._ROOM_TEMP
        logger.debug("ROOM_TEMP - %d" % y) 
        self.libtft.HLine(0, self._MAX_COLS, self._ROOM_TEMP, self.libtft.BLUE)

    def _getTime(self):
        # dtMessage = (datetime.now().strftime('%b %d  %I:%M %p\n'))
        dtMessage = (datetime.now().strftime('%I:%M %p'))
        return dtMessage

    def _getTempCPU(self):
        """Returns CPU temp in degrees F"""
        tPath = "/sys/class/thermal/thermal_zone0/temp"
        tFile = open(tPath)
        temp = tFile.read()
        tFile.close()
        return (float(temp)*0.0018 + 32)

    
    def _getTemperature(self):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        f = temperature * (9.0 / 5.0) + 32
        thMessage = "%3.1ff - %0.2f%%" % (f, humidity)
        return thMessage
   
  
    def _run(self, cmd):
        """Runs a system (bash) command"""
        return os.popen(cmd).read()

    def _getIPAddr(self):
        """Returns IP address as a string"""
        cmd = "ifconfig | awk '/192/ {print $2}'"
        res = self._run(cmd).replace("\n", "")  # remove end of line char
        return res.replace("addr:", "")  # remove "addr:" prefix

    def displayInfo(self):
        """Show IP address, CPU temp, and Time"""
        self.libtft.ClearScreen()

        self.plotTemp()
        
        tStr = self._getTime()
        temp = self._getTemperature()
        
        self.libtft.PutSt("IP   : %s" % self._getIPAddr(), 0, 0, c=self.libtft.WHITE)
        self.libtft.PutSt("Time : %s" % tStr, 0, self._FontY * 2, c=self.libtft.WHITE)
        self.libtft.PutSt("Temp : %s" % temp, 0, self._FontY * 4, c=self.libtft.WHITE)

#
# Main Program
#
if __name__ == u"__main__":

    tft = TFTGraphTemp()

    if len(sys.argv) > 1:
        tft.displayInfo()
    else:
        while True:
            tft.displayInfo()
            time.sleep(60) 
    logger.debug("Done.")


