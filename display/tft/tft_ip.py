#!/usr/bin/env python
import cooper14 as font
import font0 as font0
import RPi.GPIO as GPIO
import time
import os  # for popen
import spidev  # hardware SPI
from random import randint
from math import sqrt
from datetime import datetime
from bh1750 import *
from libtft import *
import sqlite3
import Adafruit_DHT
from Logger import *
logger = setupLogging("lcd_ip")
logger.setLevel(INFO)

# Temperature Sensor
ShowTemp = False
sensor = Adafruit_DHT.AM2302
pin = '4'
conn = sqlite3.connect("/home/pi/rpi/Weather/Weather.db") 


def Run(cmd):
    """Runs a system (bash) command"""
    return os.popen(cmd).read()


def GetIPAddr():
    """Returns IP address as a string"""
    cmd = "ifconfig | awk '/192/ {print $2}'"
    res = Run(cmd).replace("\n", "")  # remove end of line char
    return res.replace("addr:", "")  # remove "addr:" prefix

def getTemperature():
    humidity = 0
    temperature = 0
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    thMessage = "%3.1ff - %0.2f%%" % (f, humidity)
    logger.debug("tMessage : %s" % thMessage) 

    insertTemperature(conn, printOut=False)
    return thMessage


def insertTemperature(conn, printOut=False):
    id = getID(conn) + 1
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    dtMessage = getDateTime()

    qs1 = "insert into temperature_temperature (id, ReadingDateTime, TempC, TempF, Humidity) values "
    qs2 = "(%d, '%s', '%3.1f*C', '%3.1f*F', '%0.2f%%')" % (id, dtMessage, temperature, f, humidity)

    qs = qs1 + qs2

    if printOut == True:
        logger.debug(u"%s" % qs)

    cursor = conn.execute(qs)
    conn.commit()
    thMessage = ("T=%3.1ff H=%0.2f%%" % (f, humidity))
    return thMessage


def getID(conn):
    ins = "select max(id) from temperature_temperature"
    cursor = conn.execute(ins)

    for row in cursor:
        id = int(row[0])
        logger.debug("%s" % row[0])
        break
    return id


def getDateTime():
    dtMessage = (datetime.now().strftime('%b %d  %I:%M %p'))
    logger.debug("dtMessage : %s" % dtMessage) 
    return dtMessage

def getTime():
    dt = datetime.now().strftime('%I:%M')
    hour = int(dt.split(":")[0])
    minute = int(dt.split(":")[1])
    tMessage = (datetime.now().strftime('%I:%M %p'))
    return hour, minute, tMessage



def tftDisplay(libtft):
    """Show IP address, temp, and time """
    tempMsg  = getTemperature()
    logger.debug("%s" % tempMsg)

    hour, minute, timeMsg = getTime()
    logger.debug("%s" % timeMsg)

    ipMsg    = GetIPAddr()
    logger.debug("%s" % ipMsg)
   
    libtft.ClearScreen()
    
    libtft.PutString(0, 0, "IP ", libtft.YELLOW)
    libtft.PutString(0, 20, ipMsg, libtft.WHITE)

    libtft.PutString(0, 40, "Time", libtft.YELLOW)
    libtft.PutString(0, 60, timeMsg, libtft.WHITE)

    libtft.PutString(0, 80, "Temp", libtft.YELLOW)
    libtft.PutString(0, 100, tempMsg, libtft.WHITE)

    x1 = 0
    y1 = 140
    x2 = hour + x1
    y2 = minute + y1
    color = libtft.COLORSET[hour]
    libtft.DrawRect(x1, y1, x2, y2, color=color)



#
# Main Program
#
if __name__ == u"__main__":
    libtft = TFTLib()

    libtft.SetOrientation(180)

    while True:
        tftDisplay(libtft)
        time.sleep(60)

    spi.close()  # close down SPI interface

