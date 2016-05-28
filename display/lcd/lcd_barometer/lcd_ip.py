#!/usr/bin/env python
import os
import sys
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import barometric_pressure_sensor as BPS
import sqlite3
from Logger import *

logger = setupLogging(u"lcd_ip")
logger.setLevel(INFO)

wlan0_cmd = u"ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"
eth0_cmd = u"ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"

conn = sqlite3.connect(u'/home/pi/lcd/barometric_temp.db')

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


def insertBarometer(temperature, barometer):
    global conn

    hour, minute, dtMessage = getDateTime()
    TempF = temperature
    barometer = barometer

    qs = u"insert into temperature_barometer (ReadingDateTime, TempF, Barometer) values ('%s', '%s', '%s')" \
         % (dtMessage, TempF, barometer)

    conn.execute(qs)

    conn.commit()

    logger.debug(u"Success :%s" % qs)


def getDateTime():
    dt = datetime.now().strftime(u"%I:%M")
    hour = int(dt.split(u":")[0])
    minute = int(dt.split(u":")[1])
    dtMessage = (datetime.now().strftime(u"%b %d  %I:%M %p"))
    return hour, minute, dtMessage


def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output


def getIP():
    try:
        cs = run_cmd(eth0_cmd)
        ipMessage = u"IP:%s" % (cs)

        if len(cs.strip()) == 0:
            cs = run_cmd(wlan0_cmd)
            cs = cs.split(os.linesep)[0]
            ipMessage = u"IP:%s" % (cs)

    except Exception, msg:
        logger.error(u"%s" % msg)
        ipMessage = u"IP: unknown"

    logger.debug(u"%s[%d]" % (ipMessage, len(ipMessage)))

    return ipMessage


if __name__ == u"__main__":
    BackLight = True
    st = 20

    while True:
        try:

            gpio = MCP.MCP23017()
            logger.debug(u"Have gpio")

            # Initialize the LCD using the pins
            lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                          lcd_d7, lcd_columns, lcd_rows, lcd_red,
                                          lcd_green, lcd_blue, gpio=gpio)
            logger.debug(u"Have lcd")

            # Set backlight color and turn on
            lcd.clear()
            lcd.set_backlight(1)
            break

        except Exception, msg:
            logger.debug(u"%s" % msg)

    showBPS = True
    while True:
        try:
            mpl = BPS.MPL115A2(address=0x60, debug=False)
            pt = mpl.getPT()

            hour, minute, dtMessage = getDateTime()
            timeMessage = dtMessage + u"\n"
            ipMessage = getIP()

            # Display IP Address
            lcd.clear()

            if ((minute % 15) == 0):
                lcd.set_backlight(1)
            else:
                lcd.set_backlight(1)

            if showBPS is True:
                barometer = pt[0] * (760.0 / 101.325)
                fTemp = (pt[1] * (9.0 / 5.0)) + 32
                lcd.message(u"Barometer %4.3f\n" % barometer)
                lcd.message(u"Temp      %4.3f" % fTemp)
                showBPS = False

                if (minute % 30) == 0:
                    insertBarometer(fTemp, barometer)
            else:
                lcd.message(timeMessage)
                lcd.message(ipMessage)
                showBPS = True

            sleep(st)

        except Exception, msg:
            logger.error(u"%s" % msg)
            sleep(st)

