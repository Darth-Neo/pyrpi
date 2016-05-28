#!/usr/bin/env python
#
# Temp Graph
#
__author__ = "James Morris"

import os
import sys
import cooper14 as font
from libtft import TFTLib
import sqlite3

# For 1.8 TFT 128x160
MAX_COLS = 120 # 127
MAX_ROWS = 150 # 159

MAX_POINTS = 120

ROOM_TEMP  = 78
START_TEMP = 60
MAX_TEMP   = 100

OffsetX = 1 # T-B
OffsetY = 1 # L-R

ScaleX = 1
ScaleY = 1

ROTATION = 180

def getTemperatures():

    conn = sqlite3.connect('/home/pi/rpi/Weather/Weather.db')

    # ID = row[0]
    # ReadingDateTime = row[1]
    # TempC = row[2]
    # Tempf = row[3]
    # Humidity = row[4]

    ins = "select * from temperature_temperature order by ID desc"
    cursor = conn.execute(ins)

    temps = [[x[0], x[1], x[3]] for x in cursor]

    return temps

def drawTempLine(libtft, temp, color):
    global offsetX
    global offsetY
    global MAX_COLS
    global MAX_ROWS
    global START_TEMP

    print("%d:%d" % (temp, color))

    x1 = OffsetX * ScaleX
    x2 = (MAX_COLS - OffsetX) * ScaleX
    y1 = (MAX_ROWS - temp - OffsetY) * ScaleY
    y2 = y1
    libtft.Line(x1, y1, x2, y2, color)

def plotTemp(libtft):
    """Draw a series of lines on display"""
    libtft.ClearScreen()

    # libtft.LabelIt('Temps')
    libtft.SetOrientation(ROTATION)

    temps = getTemperatures()

    adjust = 20
    
    drawTempLine(libtft, MAX_TEMP, libtft.RED)
    libtft.PutSt("Max", 5, MAX_TEMP-adjust)
    
    drawTempLine(libtft, ROOM_TEMP, libtft.BLUE)
    libtft.PutSt("Room", 5, ROOM_TEMP-adjust)
    
    drawTempLine(libtft, START_TEMP, libtft.WHITE)
    libtft.PutSt("Start", 5, START_TEMP-adjust)

    adjust = 30

    libtft.DrawRect(adjust, adjust, MAX_COLS - adjust, MAX_ROWS - adjust, libtft.GREEN)

    
    x = adjust
    y = adjust
    st = "%d, %d" % (x, y)
    libtft.PutSt(st, x, y)
    libtft.DrawPixel(x, y, libtft.GREEN)
       
    x = MAX_COLS - adjust
    y = MAX_ROWS - adjust
    st = "%d, %d" % (x, y)
    libtft.PutSt(st, x, y)
    libtft.DrawPixel(x, y, libtft.GREEN)
    
    x = adjust
    y = MAX_ROWS - adjust
    st = "%d, %d" % (x, y)  
    libtft.PutSt(st, x, y)
    libtft.DrawPixel(x, y, libtft.GREEN)

    x = MAX_COLS - adjust
    y = adjust
    st = "%d, %d" % (x, y)  
    libtft.PutSt(st, x, y)
    libtft.DrawPixel(x, y, libtft.GREEN)
    

    startPoint = None 
    n = 0
    for temp in temps:
        print("%s" % temp)

        n += 1
        spaces = " " * n

        if n == MAX_POINTS:
            break

        if startPoint is None:
            point = list()
            point.append(int(temp[0]))
            point.append(int(temp[2][:-4]))
            point1 = point
            startPoint = point1
            continue
        else:
            point = list()
            point.append(int(temp[0]))
            point.append(int(temp[2][:-4]))
            point2 = point

        x1 = (n - 1) * ScaleX
        x2 = (n ) * ScaleX
        y1 = (point1[1]) * ScaleY
        y2 = (point2[1]) * ScaleY

	# print("%s\t%d:%d\t%d:%d" % (n, x1, y1, x2, y2))

        libtft.Line(x1, y1, x2, y2, libtft.YELLOW)

        point1 = point2


#
# Main Program
#
if __name__ == u"__main__":

    libtft = TFTLib()

    plotTemp(libtft)
      
    print("Done.")


