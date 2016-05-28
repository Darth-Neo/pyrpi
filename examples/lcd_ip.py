#! /usr/bin/python
import sys
import sqlite3
import Adafruit_DHT
import Adafruit_CharLCD as LCD
from subprocess import *
from time import sleep, strftime
from datetime import datetime

ShowTemp = False
sensor = Adafruit_DHT.AM2302
pin = '4'
cmd = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"

# Make list of button value, text, and backlight color.
buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
            (LCD.LEFT,   'Left'  , (1,0,0)),
            (LCD.UP,     'Up'    , (0,0,1)),
            (LCD.DOWN,   'Down'  , (0,1,0)),
            (LCD.RIGHT,  'Right' , (1,0,1)) )

def getID(conn):
    ins = "select max(id) from temperature_temperature"
    cursor = conn.execute(ins)

    for row in cursor:
        id = int(row[0])
        #print ("%s" % row[0])
        break
    return id

def insertTemperature(conn, printOut=False):

    id = getID(conn) + 1
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    dtMessage = getTime()

    qs = "insert into temperature_temperature (id, ReadingDateTime, TempC, TempF, Humidity) values (%d, '%s', '%3.1f*C', '%3.1f*F', '%0.2f%%')" % (id, dtMessage, temperature, f, humidity)
    if printOut == True:
        print qs

    cursor = conn.execute(qs)

    conn.commit()

    thMessage = ("T=%3.1ff H=%0.2f%%" % (f, humidity))

    return thMessage

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output
    
def getTemperature():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    thMessage = ("T=%3.1ff H=%0.2f%%" % (f, humidity))
    return thMessage

def getTime():
    dtMessage = (datetime.now().strftime('%b %d  %I:%M %p\n'))
    return dtMessage

def getIP():
    cs = run_cmd(cmd)
    ipMessage = "IP:%s" % (cs)
    return ipMessage
   
def checkButtonPress(lcd, buttons):
    for button in buttons:
        if lcd.is_pressed(button[0]):
	   return True
    return False
   
if __name__ == "__main__":
    conn = sqlite3.connect('/home/pi/rpi/Weather/Weather.db')
    #TS = 10
    TS = 900
        
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(1, 0, 0)
    lcd.set_backlight(1)
    countBackLight = 10

    ShowTemp = True

    n = 0    
    while True:
        dt = datetime.now().strftime('%I:%M')
        hour = int(dt.split(":")[0])
        minute = int(dt.split(":")[1])

        if minute == 0 or minute == 15 or minute == 30 or minute == 45: 
            lcd.set_backlight(1)
            lcd.set_color(1, 0, 1)
            sleep(30)
            lcd.set_backlight(0)

        n += 1
	timeMessage = getTime()
        ipMessage = getIP()
        if n % TS <> 0:
            tempMessage = getTemperature()
        else:
            n = 0
            tempMessage = insertTemperature(conn, printOut=False)

        #print("count : %d" % countBackLight)

	if countBackLight > 0:
	    countBackLight -= 1
	    lcd.set_backlight(1)
        else:
            lcd.set_backlight(0)
	
        cbp = checkButtonPress(lcd, buttons) 
        # print ("Button : %s" % cbp)

	if checkButtonPress(lcd, buttons) == True:
	    countBackLight = 10
	
	lcd.clear()
	              
	# Display Time
	lcd.message(timeMessage)
        
        if ShowTemp == True:
            # Display Temperature
            lcd.message(tempMessage)
            ShowTemp = False
        else:
            # Display IP Address
            lcd.message(ipMessage)
            ShowTemp = True
            
	sleep(1)
