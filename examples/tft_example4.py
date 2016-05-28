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

import sqlite3
import Adafruit_DHT

# Temperature Sensor
ShowTemp = False
sensor = Adafruit_DHT.AM2302
pin = '4'


# TFT to RPi connections
#  PIN TFT RPi
#  1 backlight 3v3
#  2 MISO <none>
#  3 CLK SCLK (GPIO 11)
#  4 MOSI MOSI (GPIO 10)
#  5 CS-TFT CE0
#  6 CS-CARD <none>
#  7 D/C GPIO 25
#  8 RESET GPIO 22
#  9 VCC 3V3
#  10 GND GND

DC = 24
RST = 25

XSIZE = 128
YSIZE = 160
XMAX = XSIZE-1
YMAX = YSIZE-1
X0 = XSIZE/2
Y0 = YSIZE/2

# Color constants
BLACK = 0x0000
BLUE = 0x001F
RED = 0xF800
GREEN = 0x0400
LIME = 0x07E0
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0
WHITE = 0xFFFF
PURPLE = 0x8010
NAVY = 0x0010
TEAL = 0x0410
OLIVE = 0x8400
MAROON = 0x8000
SILVER = 0xC618
GRAY = 0x8410
bColor = BLACK
fColor = YELLOW
COLORSET = [BLACK, BLUE, RED, GREEN, LIME, CYAN, MAGENTA, YELLOW,
            WHITE, PURPLE, NAVY, TEAL, OLIVE, MAROON, SILVER, GRAY]

# TFT display constants
SWRESET = 0x01
SLPIN = 0x10
SLPOUT = 0x11
PTLON = 0x12
NORON = 0x13
INVOFF = 0x20
INVON = 0x21
DISPOFF = 0x28
DISPON = 0x29
CASET = 0x2A
RASET = 0x2B
RAMWR = 0x2C
RAMRD = 0x2E
PTLAR = 0x30
MADCTL = 0x36
COLMOD = 0x3A

#
# Low-level routines
#


def SetPin(pinNumber, value):
    # sets the GPIO pin to desired value (1=on,0=off)
    GPIO.output(pinNumber, value)


def InitGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(DC, GPIO.OUT)
    GPIO.setup(RST, GPIO.OUT)
    GPIO.output(RST, GPIO.LOW)
    GPIO.output(RST, GPIO.HIGH)


def InitSPI():
    """returns an opened spi connection to device(0,0) in mode 0"""
    spiObject = spidev.SpiDev()
    spiObject.open(0, 0)
    spiObject.mode = 0
    return spiObject

#
# ST7735 TFT controller routines:
#


def WriteByte(value):
    """sends an 8-bit value to the display as data"""
    SetPin(DC, 1)
    spi.writebytes([value])


def WriteWord(value):
    """sends a 16-bit value to the display as data"""
    SetPin(DC, 1)
    spi.writebytes([value >> 8, value & 0xFF])


def Command(cmd, *bytes):
    """Sends a command followed by any data it requires"""
    SetPin(DC, 0)  # command follows
    spi.writebytes([cmd])  # send the command byte
    if len(bytes) > 0:  # is there data to follow command?
        SetPin(DC, 1)  # data follows
        spi.writebytes(list(bytes))  # send the data bytes


def InitDisplay():
    """Resets & prepares display for active use."""
    Command(SWRESET)  # reset TFT controller
    time.sleep(0.2)  # wait 200mS for controller init
    Command(SLPOUT)  # wake from sleep
    Command(COLMOD, 0x05)  # set color mode to 16 bit
    Command(DISPON)  # turn on display


def SetOrientation(degrees):
    """Set the display orientation to 0,90,180,or 270 degrees"""
    if degrees == 90:
        arg = 0x60
    elif degrees == 180:
        arg = 0xC0
    elif degrees == 270:
        arg = 0xA0
    else:
        arg = 0x00
    Command(MADCTL, arg)


def SetAddrWindow(x0, y0, x1, y1):
    """sets a rectangular display window into which pixel data is placed"""
    Command(CASET, 0, x0, 0, x1)  # set column range (x0,x1)
    Command(RASET, 0, y0, 0, y1)  # set row range (y0,y1)


def WriteBulk(value, reps, count=1):
    """sends a 16-bit pixel word many, many times using hardware SPI
    number of writes = reps * count. Value of reps must be <= 2048"""
    SetPin(DC, 0)  # command follows
    spi.writebytes([RAMWR])  # issue RAM write command
    SetPin(DC, 1)  # data follows
    valHi = value >> 8  # separate color into two bytes
    valLo = value & 0xFF
    byteArray = [valHi, valLo]*reps  # create buffer of multiple pixels
    for a in range(count):
        spi.writebytes(byteArray)  # send this buffer multiple times


def WritePixels(byteArray):
    """sends pixel data to the TFT"""
    SetPin(DC, 0)  # command follows
    spi.writebytes([RAMWR])  # issue RAM write command
    SetPin(DC, 1)  # data follows
    spi.writebytes(byteArray)  # send data to the TFT

#
# Graphics routines:
#


def FillRect(x0, y0, x1, y1, color):
    """fills rectangle with given color"""
    width = x1-x0+1
    height = y1-y0+1
    SetAddrWindow(x0, y0, x1, y1)
    WriteBulk(color, width, height)


def FillScreen(color):
    """Fills entire screen with given color"""
    FillRect(0, 0, XMAX, YMAX, color)


def ClearScreen():
    """Fills entire screen with black"""
    FillScreen(BLACK)

#
# Text routines:
#


def GetCharData(ch):
    """Returns array of raster data for a given ASCII character"""
    pIndex = ord(ch)-ord(' ')
    lastDescriptor = len(font.descriptor)-1
    charIndex = font.descriptor[pIndex][1]
    if (pIndex >= lastDescriptor):
        return font.rasterData[charIndex:]
    else:
        nextIndex = font.descriptor[pIndex+1][1]
        return font.rasterData[charIndex:nextIndex]


def GetCharWidth(ch):
    """returns the width of a character, in pixels"""
    pIndex = ord(ch) - ord(' ')
    return font.descriptor[pIndex][0]


def GetCharHeight(ch):
    """returns the height of a character, in pixels"""
    return font.fontInfo[0]


def GetStringWidth(st):
    """returns the width of the text, in pixels"""
    width = 0
    for ch in st:
        width += GetCharWidth(ch) + 1
    return width


def PutCh(ch, xPos, yPos, color=fColor):
    """write ch to X,Y coordinates using ASCII 5x7 font"""
    charData = font0.data[ord(ch)-32]
    SetAddrWindow(xPos, yPos, xPos+4, yPos+6)
    SetPin(DC, 0)
    spi.writebytes([RAMWR])
    SetPin(DC, 1)
    buf = []
    mask = 0x01
    for row in range(7):
        for col in range(5):
            bit = charData[col] & mask
            if (bit == 0):
                pixel = bColor
            else:
                pixel = color
            buf.append(pixel >> 8)
            buf.append(pixel & 0xFF)
        mask <<= 1
    spi.writebytes(buf)


def PutCharV2(ch, xPos, yPos, color=fColor):
    """Writes Ch to X,Y coordinates in current foreground color"""
    charData = GetCharData(ch)
    xLen = GetCharWidth(ch)
    numRows = GetCharHeight(ch)
    bytesPerRow = 1+((xLen-1)/8)
    numBytes = numRows * bytesPerRow
    SetAddrWindow(xPos, yPos, xPos+xLen-1, yPos+numRows-1)
    SetPin(DC, 0)
    spi.writebytes([RAMWR])
    SetPin(DC, 1)
    i = 0
    while (i < numBytes):
        mask = 0x01
        rowBits = 0
        for b in range(bytesPerRow):
            rowBits <<= 8
            mask <<= 8
            rowBits += charData[i]
            i += 1
        mask >>= 1
        # at this point, all bits for current row should
        # be in rowBits, regardless of number of bytes
        # it takes to represent the row
        rowBuf = []
        for a in range(xLen):
            bit = rowBits & mask
            mask >>= 1
            if (bit == 0):
                pixel = bColor
            else:
                pixel = color
            rowBuf.append(pixel >> 8)
            rowBuf.append(pixel & 0xFF)
        spi.writebytes(rowBuf)


def PutChar(ch, xPos, yPos, color=fColor):
    """Writes Ch to X,Y coordinates in current foreground color"""
    charData = GetCharData(ch)
    xLen = GetCharWidth(ch)  # char width, in pixels
    numRows = GetCharHeight(ch)
    bytesPerRow = 1 + ((xLen-1)/8)  # char width, in bytes
    numBytes = numRows * bytesPerRow
    SetAddrWindow(xPos, yPos, xPos+xLen-1, yPos+numRows-1)
    SetPin(DC, 0)
    spi.writebytes([RAMWR])  # pixel data to follow
    SetPin(DC, 1)
    index = 0
    buf = []
    for a in range(numRows):  # row major
        bitNum = 0
        for b in range(bytesPerRow):  # do whole row
            mask = 0x80  # msb first
            for c in range(8):  # do all bits in this byte
                if (bitNum < xLen):  # still within char width?
                    bit = charData[index] & mask
                    if (bit == 0):  # check the bit
                        pixel = bColor  # 0: background color
                    else:
                        pixel = color  # 1: foreground color
                    buf.append(pixel >> 8)  # add pixel to buffer
                    buf.append(pixel & 0xFF)
                    mask >>= 1  # goto next bit in byte
                bitNum += 1  # goto next bit in row
            index += 1  # goto next byte of data
    spi.writebytes(buf)  # send char data to TFT


def PutString(xPos, yPos, st, color=fColor):
    """Draws string on display at xPos,yPos.
    Does NOT check to see if it fits!"""
    for ch in st:
        width = GetCharWidth(ch)+1
        PutChar(ch, xPos, yPos, color)
        xPos += width

#
# Testing routines:
#


def PrintElapsedTime(function, startTime):
    """Formats an output string showing elapsed time since function start"""
    elapsedTime = time.time() - startTime
    print("%15s: %8.3f seconds" % (function, elapsedTime))
    time.sleep(1)


def ColorBars():
    """Fill Screen with 8 color bars"""
    for a in range(8):
        FillRect(0, a*20, XMAX, a*20+19, COLORSET[a+1])


def ScreenTest():
    """Measures time required to fill display twice"""
    startTime = time.time()
    FillScreen(LIME)
    FillScreen(MAGENTA)
    ColorBars()
    PrintElapsedTime("ScreenTest", startTime)


def PortaitChars():
    """Writes 420 characters (5x7) to screen in Portrait Mode"""
    # font is 5x7 with 1 pixel spacing
    # so character width = 6 pixels, height = 8 pixels
    # display width = 128 pixels, so 21 char per row (21x6 = 126)
    # display ht = 160 pixels, so 20 rows (20x8 = 160)
    # total number of characters = 21 x 20 = 420
    CHARS_PER_ROW = 21
    FillRect(0, 0, XMAX, YMAX, bColor)  # clear screen
    for i in range(420):
        x = i % CHARS_PER_ROW
        y = i / CHARS_PER_ROW
        ascii = (i % 96)+32
        PutCh(chr(ascii), x*6, y*8)
    time.sleep(1)


def LandscapeChars():
    """Writes 416 characters (5x7) to screen, landscape mode"""
    # font is 5x7 with 1 pixel spacing
    # so character width = 6 pixels, height = 8 pixels
    # display width = 160 pixels, so 26 char per row (26x6 = 156)
    # display ht = 128 pixels, so 16 rows (16x8 = 128)
    # total number of characters = 26 x 16 = 416
    CHARS_PER_ROW = 26
    FillRect(0, 0, YMAX, XMAX, bColor)  # clear screen
    for i in range(416):
        x = i % CHARS_PER_ROW
        y = i / CHARS_PER_ROW
        ascii = (i % 96)+32
        PutCh(chr(ascii), x*6, y*8, CYAN)
    time.sleep(1)


def LargeFontTest():
    """Writes 90 characters (11x17) to the screen"""
    title = "Large Font"
    startTime = time.time()
    for i in range(90):
        x = i % 10
        y = i / 10
        ascii = (i % 96) + 32
        PutChar(chr(ascii), x*12, y*18, LIME)
    PrintElapsedTime(title, startTime)


def RandColor():
    """Returns a random color from BGR565 Colorspace"""
    index = randint(0, len(COLORSET)-1)
    return COLORSET[index]


def SmallFontTest():
    """Writes 2000 random 5x7 characters to the screen"""
    title = "Small Font"
    startTime = time.time()
    for i in range(2000):
        x = randint(0, 20)
        y = randint(0, 19)
        color = RandColor()
        ascii = (i % 96)+32
        PutCh(chr(ascii), x*6, y*8, color)
    PrintElapsedTime(title, startTime)


def OrientationTest():
    """Write 5x7 characters at 0,90,180,270 deg orientations"""
    title = "Orientation"
    startTime = time.time()
    PortaitChars()
    SetOrientation(90)  # display-top on right
    LandscapeChars()
    SetOrientation(180)  # upside-down
    PortaitChars()
    SetOrientation(270)  # display-top on left
    LandscapeChars()
    SetOrientation(0)  # return to 0 deg.
    PrintElapsedTime(title, startTime)


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


def InfoTest():
    ClearScreen()
    """Show IP address, CPU temp, and Time"""
    title = "Info"
    startTime = time.time()
    PutString(0, 0, "IP addr", WHITE)
    PutString(0, 20, GetIPAddr())
    PutString(0, 60, "Temp", WHITE)

    if False:
        temp = GetTempCPU()
        PutString(0, 80, "%5.1f deg F" % (temp))
    else:
        msg = getTemperature()
        PutString(0, 80, "%s" % (msg))

    # tStr = time.strftime("%I:%M:%S ")
    tStr = getTime()
    PutString(0, 120, "Time", WHITE)
    PutString(0, 140, tStr)
    PrintElapsedTime(title, startTime)


def RunTextTests():
    ClearScreen()
    startTime = time.time()  # keep track of test duration
    ScreenTest()
    LargeFontTest()
    SmallFontTest()
    OrientationTest()
    InfoTest()
    PrintElapsedTime("Full Suite", startTime)


def getTemperature():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f = temperature * (9.0 / 5.0) + 32
    thMessage = "%3.1ff - %0.2f%%" % (f, humidity)
    return thMessage


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


def getID(conn):
    ins = "select max(id) from temperature_temperature"
    cursor = conn.execute(ins)

    for row in cursor:
        id = int(row[0])
        #print ("%s" % row[0])
        break
    return id

def getTime():
    # dtMessage = (datetime.now().strftime('%b %d  %I:%M %p\n'))
    dtMessage = (datetime.now().strftime('%I:%M %p'))
    return dtMessage

#
# Main Program
#
if __name__ == u"__main__":
    print("Adafruit 1.8 TFT display demo with hardware SPI")
    spi = InitSPI()  # initialize SPI interface
    InitGPIO()  # initialize GPIO interface
    InitDisplay()  # initialize TFT controller
    # RunTextTests()  # run suite of text tests
    InfoTest()
    spi.close()  # close down SPI interface

