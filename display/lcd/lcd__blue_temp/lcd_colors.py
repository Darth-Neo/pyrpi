#! /usr/bin/python

import sys
import Adafruit_CharLCD as LCD
from time import sleep, strftime

if __name__ == "__main__":

    # Sleep time
    TS = 1
 
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.clear()
    lcd.set_color(0, 0, 0)
    lcd.set_backlight(1)
    lcd.message("Hello World\n0 : 0 : 0")

    for r in range(0, 2):
        for g in range(0, 2):
            for b in range(0, 2):
                lcd.clear()
                lcd.set_color(r, g, b)
                color = "Hello Megan\n%d : %d : %d" % (r,g,b)  
                lcd.message(color)
                print("%d : %d : %d" % (r,g,b))
                sleep(TS)
