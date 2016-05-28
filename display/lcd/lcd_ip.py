#!/usr/bin/env python
import os
import sys
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import Adafruit_CharLCD as LCD

from Logger import *
logger = setupLogging("lcd_ip")
logger.setLevel(DEBUG)

wlan0_cmd = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"
eth0_cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"


# Make list of button value, text, and backlight color.
buttons = ((LCD.SELECT, 'Select', (1, 1, 1)),
           (LCD.LEFT, 'Left', (1, 0, 0)),
           (LCD.UP, 'Up', (0, 0, 1)),
           (LCD.DOWN, 'Down', (0, 1, 0)),
           (LCD.RIGHT, 'Right', (1, 0, 1)))


def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output


def getTime():
    dtMessage = (datetime.now().strftime('%b %d  %I:%M %p\n'))
    return dtMessage


def GetIPAddr():
    """Returns IP address as a string"""
    cmd = "ifconfig | awk '/192/ {print $2}'"
    res = Run(cmd).replace("\n", "")  # remove end of line char
    return res.replace("addr:", "")  # remove "addr:" prefix


def getIP():
    cs = run_cmd(eth0_cmd)
    ipMessage = "IP:%s" % (cs)

    if len(cs.strip()) == 0:
       cs = run_cmd(wlan0_cmd)
       ipMessage = "IP:%s" % (cs)

    logger.debug("%s[%d]" % (ipMessage, len(ipMessage)))

    return ipMessage


def checkButtonPress(lcd, buttons):
    for button in buttons:
        if lcd.is_pressed(button[0]):
            return True
    return False

    
if __name__ == "__main__":
  
  while True:
    try:
      lcd = LCD.Adafruit_CharLCDPlate()

      # Set backlight color and turn on
      lcd.clear()
      lcd.set_backlight(1)
      lcd.set_color(1, 0, 0)
      break
    
    except Exception, msg:
      logger.debug(u"%s" % msg)

    n = 0
  while True:
    try:
	dt = datetime.now().strftime('%I:%M')
	hour = int(dt.split(":")[0])
	minute = int(dt.split(":")[1])
	
	timeMessage = getTime()
	ipMessage = getIP()

	# Display IP Address
	lcd.clear()
	lcd.set_color(1, 0, 0)
	lcd.message(timeMessage)
	lcd.message(ipMessage)

	sleep(60)
        
    except Exception, msg:
	logger.debug(u"%s" % msg)
	sleep(60)
