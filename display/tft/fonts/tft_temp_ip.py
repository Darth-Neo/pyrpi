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

# Temperature Sensor
ShowTemp = False
sensor = Adafruit_DHT.AM2302
pin = '4'
conn = sqlite3.connect('/home/pi/rpi/Weather/Weather.db') 

def GetTempCPU():
    """Returns CPU temp in degrees F"""
    tPath = "/sys/class/thermal/thermal_zone0/temp"
    tFile = open(tPath)
    temp = tFile.read()
    tFile.close()
    return (float(temp)*0.0018 + 32)


def Run(cmd):
    """Runs a system (bash) command"""
    return os.popen(cmd).read()


def GetIPAddr():
    """Returns IP address as a string"""
    cmd = "ifconfig | awk '/192/ {print $2}'"
    res = Run(cmd).replace("\n", "")  # remove end of line char
    return res.replace("addr:", "")  # remove "addr:" prefix


def tftDisplay(libtft):
    """Show IP address, temp, and time """
    tempMsg  = getTemperature()
    print("%s" % tempMsg)

    timeMsg  = getTime()
    print("%s" % timeMsg)

    ipMsg    = GetIPAddr()
    print("%s" % ipMsg)

    lightMsg = "UKN" #getLight()
    print("%s" % lightMsg)
   
    libtft.ClearScreen()
    
    libtft.PutString(0, 0, "IP ", libtft.YELLOW)
    libtft.PutString(0, 20, ipMsg, libtft.WHITE)

    libtft.PutString(0, 40, "Time", libtft.YELLOW)
    libtft.PutString(0, 60, timeMsg, libtft.WHITE)

    libtft.PutString(0, 80, "Temp", libtft.YELLOW)
    libtft.PutString(0, 100, tempMsg, libtft.WHITE)


def getTemperature():
    humidity = 0
    temperature = 0
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    thMessage = "%3.1ff - %0.2f%%" % (f, humidity)
    print("tMessage : %s" % thMessage) 

    insertTemperature(conn, printOut=False)
    return thMessage


def insertTemperature(conn, printOut=False):
    id = getID(conn) + 1
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    dtMessage = getDateTime()

    qs = "insert into temperature_temperature (id, ReadingDateTime, TempC, TempF, Humidity) values (%d, '%s', '%3.1f*C', '%3.1f*F', '%0.2f%%')" % (id, dtMessage, temperature, f, humidity)
    if printOut == True:
        print qs

    cursor = conn.execute(qs)
    conn.commit()
    thMessage = ("T=%3.1ff H=%0.2f%%" % (f, humidity))
    return thMessage


def getID(conn):
    ins = "select max(id) from temperature_temperature"
    cursor = conn.execute(ins)

    for row in cursor:
        id = int(row[0])
        print ("%s" % row[0])
        break
    return id


def getDateTime():
    dtMessage = (datetime.now().strftime('%b %d  %I:%M %p'))
    print("dtMessage : %s" % dtMessage) 
    return dtMessage

def getTime():
    tMessage = (datetime.now().strftime('%I:%M %p'))
    return tMessage

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

