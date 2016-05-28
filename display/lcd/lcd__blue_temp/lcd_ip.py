#!/usr/bin/env python
import os
import sys
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import Adafruit_CharLCD as LCD
# import Adafruit_GPIO.MCP230xx as MCP
import sqlite3
from Logger import *

logger = setupLogging(u"lcd_ip")
logger.setLevel(DEBUG)

wlan0_cmd = u"ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"
eth0_cmd = u"ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"

# Define MCP pins connected to the LCD.
lcd_rs = 0
lcd_en = 1
lcd_d4 = 2
lcd_d5 = 3
lcd_d6 = 4
lcd_d7 = 5
lcd_red = 6
lcd_green = 7
lcd_blue = 8

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2


def getDateTime():
    dt = datetime.now().strftime(u"%I:%M")
    hour = int(dt.split(u":")[0])
    minute = int(dt.split(u":")[1])
    dtMessage = (datetime.now().strftime(u"%b %d  %I:%M %p"))
    return hour, minute, dtMessage


def Run(cmd):
    """Runs a system (bash) command"""
    return os.popen(cmd).read()


def getIP():
    try:
        cs = Run(eth0_cmd)
        ipMessage = u"IP:%s" % (cs)

        if len(cs.strip()) == 0:
            cs = Run(wlan0_cmd)
            cs = cs.split(os.linesep)[0]
            ipMessage = u"IP:%s" % (cs)

    except Exception, msg:
        logger.error(u"%s" % msg)
        ipMessage = u"IP: unknown"

    logger.debug(u"%s[%d]" % (ipMessage, len(ipMessage)))

    return ipMessage


if __name__ == u"__main__":
    st = 20

    try: 
        if True:
            lcd = LCD.Adafruit_CharLCDPlate()
        else:
            gpio = MCP.MCP23017()
            logger.debug(u"Have gpio")
            # Initialize the LCD using the pins
            lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                              lcd_d7, lcd_columns, lcd_rows, lcd_red,
                                              lcd_green, lcd_blue, gpio=gpio)

        logger.debug(u"Have lcd. follow the white rabbit")

        # Set backlight color and turn on
        lcd.clear()
        lcd.set_color(1, 0, 0) 
        lcd.set_backlight(1)

    except Exception, msg:
        logger.debug(u"%s" % msg)

    while True:
        try:
            hour, minute, dtMessage = getDateTime()
            timeMessage = dtMessage + u"\n"
            ipMessage = getIP()

            # Display IP Address
            lcd.clear()
            lcd.set_color(1, 0, 0) 

            # if ((minute % 15) == 0):
            #    lcd.set_backlight(1)
            # else:
            #    lcd.set_backlight(1)

            lcd.message(timeMessage)
            logger.debug(u"%s" % timeMessage[:-1])

            lcd.message(ipMessage)
            logger.debug(u"%s" % ipMessage[:-1])

            sleep(st)

        except Exception, msg:
            logger.error(u"%s" % msg)
            sleep(st)

