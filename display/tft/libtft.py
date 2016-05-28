#!/usr/bin/env python 
# DarthNeo

import cooper14 as font
import font5x7 as font0

import RPi.GPIO as GPIO
import time
import os  # for popen
import spidev  # hardware SPI
from random import randint
from math import sqrt, sin, cos
from datetime import datetime
from struct import unpack_from

import sqlite3
import Adafruit_DHT

from Logger import *
logger = setupLogging("libtft")
logger.setLevel(INFO)

BLACK = 0x0000


#
# Main class to make life easier
#
class TFTLib(object):
    # Temperature Sensor
    ShowTemp = False
    sensor = Adafruit_DHT.AM2302
    pin = '4'

    INT4 = '<l'  # get 4-byte word from unpacking routine
    INT2 = '<h'  # get 2-byte word from unpacking routine

    # TFT to RPi connections
    #  PIN TFT RPi
    #  1 backlight  3v3
    #  2 MISO       <none>
    #  3 CLK        SCLK (GPIO 11)
    #  4 MOSI       MOSI (GPIO 10)
    #  5 CS-TFT     CE0
    #  6 CS-CARD    <none>
    #  7 D/C        GPIO24
    #  8 RESET      GPIO25
    #  9 VCC        3V3
    #  10 GND       GND

    DC = 24
    RST = 25

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
    GAMSET = 0x36
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E
    PTLAR = 0x30
    MADCTL = 0x36
    COLMOD = 0x3A
    FRMCT1 = 0xB1
    FRMCT2 = 0xB2
    FRMCT3 = 0xB3
    INVCTR = 0xB4
    DISSET = 0xB6
    PWRCT1 = 0xC0
    PWRCT2 = 0xC1
    PWRCT3 = 0xC2
    PWRCT4 = 0xC3
    PWRCT5 = 0xC4
    VMCTR1 = 0xC5
    PWRCT6 = 0xFC
    GAMCTP = 0xE0
    GAMCTN = 0xE1

    def __init__(self):
        self.spi = self._InitSPI()  # initialize SPI interface
        self._InitGPIO()  # initialize GPIO interface
        self._InitDisplay(True)  # initialize TFT controller
        self.bColor = self.BLACK

        self.XSIZE = 128
        self.YSIZE = 160
        self.XMAX = self.XSIZE - 1
        self.YMAX = self.YSIZE - 1
        self.X0 = self.XSIZE / 2
        self.Y0 = self.YSIZE / 2

    def __del__(self):
        self.spi.close()  # close down SPI interface

    #
    # Low-level routines
    #

    def _SetPin(self, pinNumber, value):
        # sets the GPIO pin to desired value (1=on,0=off)
        GPIO.output(pinNumber, value)

    def _InitGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DC, GPIO.OUT)
        GPIO.setup(self.RST, GPIO.OUT)
        GPIO.output(self.RST, GPIO.LOW)
        GPIO.output(self.RST, GPIO.HIGH)

    def _InitSPI(self):
        """returns an opened spi connection to device(0,0) in mode 0"""
        spiObject = spidev.SpiDev()
        spiObject.open(0, 0)
        spiObject.mode = 0
        return spiObject

    #
    # ST7735 TFT controller routines:
    #

    def _WriteByte(self, value):
        """sends an 8-bit value to the display as data"""
        self._SetPin(self.DC, 1)
        self.spi.writebytes([value])

    def _WriteWord(self, value):
        """sends a 16-bit value to the display as data"""
        self._SetPin(self.DC, 1)
        self.spi.writebytes([value >> 8, value & 0xFF])

    def _Command(self, cmd, *bytes):
        """Sends a command followed by any data it requires"""
        self._SetPin(self.DC, 0)  # command follows
        self.spi.writebytes([cmd])  # send the command byte
        if len(bytes) > 0:  # is there data to follow command?
            self._SetPin(self.DC, 1)  # data follows
            self.spi.writebytes(list(bytes))  # send the data bytes

    def _InitDisplay(self, fullReset=False):
        """Resets & prepares display for active use."""
        self._Command(self.SWRESET)  # reset TFT controller
        time.sleep(0.2)  # wait 200mS for controller init
        self._Command(self.SLPOUT)  # wake from sleep
        self._Command(self.COLMOD, 0x05)  # set color mode to 16 bit

        if fullReset:
            self._Command(self.FRMCT1, 0x01, 0x2C, 0x2D)
            self._Command(self.FRMCT2, 0x01, 0x2C, 0x2D)
            self._Command(self.FRMCT3, 0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D)
            self._Command(self.INVCTR, 0x07)
            self._Command(self.PWRCT1, 0xA2, 0x02, 0x84)
            self._Command(self.PWRCT2, 0xC5)
            self._Command(self.PWRCT3, 0x0A, 0x00)
            self._Command(self.PWRCT4, 0x8A, 0x2A)
            self._Command(self.PWRCT5, 0x8A, 0xEE)
            self._Command(self.VMCTR1, 0x0E)
            self._Command(self.MADCTL, 0x00)
            self._Command(self.GAMCTP, 0x02, 0x1C, 0x07, 0x12, 0x37, 0x32, 0x29, 0x2D,
                          0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10)
            self._Command(self.GAMCTN, 0x03, 0x1D, 0x07, 0x06, 0x2E, 0x2C, 0x29, 0x2D,
                          0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10)
            self._Command(self.NORON)
        self._Command(self.DISPON)  # turn on display

    def SetOrientation(self, degrees):
        """Set the display orientation to 0,90,180,or 270 degrees"""
        if degrees == 90:
            arg = 0x60
        elif degrees == 180:
            arg = 0xC0
        elif degrees == 270:
            arg = 0xA0
        else:
            arg = 0x00
        self._Command(self.MADCTL, arg)

    def _SetAddrWindow(self, x0, y0, x1, y1):
        """sets a rectangular display window into which pixel data is placed"""
        self._Command(self.CASET, 0, x0, 0, x1)  # set column range (x0,x1)
        self._Command(self.RASET, 0, y0, 0, y1)  # set row range (y0,y1)

    def _WriteBulk(self, value, reps, count=1):
        """sends a 16-bit pixel word many, many times using hardware SPI
        number of writes = reps * count. Value of reps must be <= 2048"""
        self._SetPin(self.DC, 0)  # command follows
        self.spi.writebytes([self.RAMWR])  # issue RAM write command
        self._SetPin(self.DC, 1)  # data follows
        valHi = value >> 8  # separate color into two bytes
        valLo = value & 0xFF
        byteArray = [valHi, valLo] * reps  # create buffer of multiple pixels
        for a in range(count):
            self.spi.writebytes(byteArray)  # send this buffer multiple times

    def _WritePixels(self, byteArray):
        """sends pixel data to the TFT"""
        self._SetPin(self.DC, 0)  # command follows
        self.spi.writebytes([self.RAMWR])  # issue RAM write command
        self._SetPin(self.DC, 1)  # data follows
        self.spi.writebytes(byteArray)  # send data to the TFT

    ########################################################################
    #
    # Graphics routines:
    #
    #
    def DrawPixel(self, x, y, color):
        """draws a pixel on the TFT display"""
        self._SetAddrWindow(x, y, x, y)
        self._Command(self.RAMWR, color >> 8, color & 0xFF)

    def SetPixel(self, x, y, color):
        """draws a pixel on the TFT display; increases speed by inlining"""
        GPIO.output(self.DC, 0)
        self.spi.writebytes([self.CASET])
        GPIO.output(self.DC, 1)
        self.spi.writebytes([0, x, 0, x])
        GPIO.output(self.DC, 0)
        self.spi.writebytes([self.RASET])
        GPIO.output(self.DC, 1)
        self.spi.writebytes([0, y, 0, y])
        GPIO.output(self.DC, 0)
        self.spi.writebytes([self.RAMWR])
        GPIO.output(self.DC, 1)
        self.spi.writebytes([color >> 8, color & 0xFF])

    def HLine(self, x0, x1, y, color):
        """draws a horizontal line in given color"""
        width = x1 - x0 + 1
        self._SetAddrWindow(x0, y, x1, y)
        self._WriteBulk(color, width)

    def VLine(self, x, y0, y1, color):
        """draws a verticle line in given color"""
        height = y1 - y0 + 1
        self._SetAddrWindow(x, y0, x, y1)
        self._WriteBulk(color, height)

    def Line(self, x0, y0, x1, y1, color):
        """draws a line in given color"""
        if (x0 == x1):
            self.VLine(x0, y0, y1, color)
        elif (y0 == y1):
            self.HLine(x0, x1, y0, color)
        else:
            slope = float(y1 - y0) / (x1 - x0)
            if (abs(slope) < 1):
                for x in range(x0, x1 + 1):
                    y = (x - x0) * slope + y0
                    self.SetPixel(x, int(y + 0.5), color)
            else:
                for y in range(y0, y1 + 1):
                    x = (y - y0) / slope + x0
                    self.SetPixel(int(x + 0.5), y, color)

    def DrawRect(self, x0, y0, x1, y1, color):
        """Draws a rectangle in specified color"""
        self.HLine(x0, x1, y0, color)
        self.HLine(x0, x1, y1, color)
        self.VLine(x0, y0, y1, color)
        self.VLine(x1, y0, y1, color)

    def FillRect(self, x0, y0, x1, y1, color):
        """fills rectangle with given color"""
        width = x1 - x0 + 1
        height = y1 - y0 + 1
        self._SetAddrWindow(x0, y0, x1, y1)
        self._WriteBulk(color, width, height)

    def FillScreen(self, color):
        """Fills entire screen with given color"""
        self.FillRect(0, 0, self.XMAX, self.YMAX, color)

    def ClearScreen(self):
        """Fills entire screen with black"""
        self.FillScreen(self.BLACK)  # alternative: bColor for background

    def Circle(self, x0, y0, radius, color=fColor):
        """draws circle at x0,y0 with given radius & color"""
        xEnd = int(0.7071 * radius) + 1
        for x in range(xEnd):
            y = int(sqrt(radius * radius - x * x))
            self.SetPixel(x0 + x, y0 + y, color)
            self.SetPixel(x0 + x, y0 - y, color)
            self.SetPixel(x0 - x, y0 + y, color)
            self.SetPixel(x0 - x, y0 - y, color)
            self.SetPixel(x0 + y, y0 + x, color)
            self.SetPixel(x0 + y, y0 - x, color)
            self.SetPixel(x0 - y, y0 + x, color)
            self.SetPixel(x0 - y, y0 - x, color)

    def FastCircle(self, x0, y0, radius, color=fColor):
        """draws circle at x0,y0 with given radius & color"
        "using the 'Midpoint Circle Algoritm'"""
        x = radius
        y = 0
        radiusError = 1 - x
        while x >= y:
            self.SetPixel(x0 + x, y0 + y, color)
            self.SetPixel(x0 + x, y0 - y, color)
            self.SetPixel(x0 - x, y0 + y, color)
            self.SetPixel(x0 - x, y0 - y, color)
            self.SetPixel(x0 + y, y0 + x, color)
            self.SetPixel(x0 + y, y0 - x, color)
            self.SetPixel(x0 - y, y0 + x, color)
            self.SetPixel(x0 - y, y0 - x, color)
            y += 1
            if radiusError < 0:
                radiusError += 2 * y + 1
            else:
                x -= 1
                radiusError += 2 * (y - x + 1)

    def FillCircle(self, x0, y0, radius, color=fColor):
        """draws filled circle at x,y with given radius & color"""
        r2 = radius * radius
        for x in range(radius):
            y = int(sqrt(r2 - x * x))
            self.VLine(x0 + x, y0 - y, y0 + y, color)
            self.VLine(x0 - x, y0 - y, y0 + y, color)

    def Ellipse(self, x0, y0, width, height, color=fColor):
        """draws an ellipse of given width & height"
        "two-part Bresenham method"""
        a = width / 2  # divide by 2, for x-radius
        b = height / 2  # divide by 2, for y-radius
        a2 = a * a
        b2 = b * b

        x = 0
        y = b
        sigma = 2 * b2 + a2 * (1 - 2 * b)
        while b2 * x <= a2 * y:
            self.SetPixel(x0 + x, y0 + y, color)
            self.SetPixel(x0 + x, y0 - y, color)
            self.SetPixel(x0 - x, y0 + y, color)
            self.SetPixel(x0 - x, y0 - y, color)
            if sigma >= 0:
                sigma += 4 * a2 * (1 - y)
                y -= 1
            sigma += b2 * (4 * x + 6)
            x += 1
        x = a
        y = 0
        sigma = 2 * a2 + b2 * (1 - 2 * a)
        while a2 * y <= b2 * x:
            self.SetPixel(x0 + x, y0 + y, color)
            self.SetPixel(x0 + x, y0 - y, color)
            self.SetPixel(x0 - x, y0 + y, color)
            self.SetPixel(x0 - x, y0 - y, color)
            if sigma >= 0:
                sigma += 4 * b2 * (1 - x)
                x -= 1
            sigma += a2 * (4 * y + 6)
            y += 1

    def VBar(self, x, y, width, height, prevHt=0, color=fColor):
        """draws a vertical bar of given height & color"""
        if height > 0:
            if prevHt == 0:
                self.FillRect(x, y - height, x + width, y, color)
            elif height > prevHt:
                self.FillRect(x, y - height, x + width, y - prevHt, color)
            else:
                self.FillRect(x, y - prevHt, x + width, y - height, self.bColor)

    def FillEllipse(self, xPos, yPos, width, height, color):
        """draws a filled ellipse of given width & height"""
        a = width / 2  # divide by 2, for x-radius
        b = height / 2  # divide by 2, for y-radius
        b2 = b * b
        a2 = a * a
        a2b2 = a2 * b2
        x0 = a
        dx = 0
        self.HLine(xPos - a, xPos + a, yPos, color)
        for y in range(1, b + 1):
            x1 = x0 - (dx - 1)
            for x1 in range(x1, 0, -1):
                if x1 * x1 * b2 + y * y * a2 <= a2b2:
                    break
            dx = x0 - x1
            x0 = x1
            self.HLine(xPos - x0, xPos + x0, yPos + y, color)
            self.HLine(xPos - x0, xPos + x0, yPos - y, color)

    ########################################################################
    #
    # Text routines:
    #

    #
    # font
    #
    def _GetCharData(self, ch):
        """Returns array of raster data for a given ASCII character"""
        pIndex = ord(ch) - ord(' ')
        lastDescriptor = len(font.descriptor) - 1
        charIndex = font.descriptor[pIndex][1]

        if (pIndex >= lastDescriptor):
            return font.rasterData[charIndex:]
        else:
            nextIndex = font.descriptor[pIndex + 1][1]
            return font.rasterData[charIndex:nextIndex]

    def _GetCharWidth(self, ch):
        """returns the width of a character, in pixels"""
        pIndex = ord(ch) - ord(' ')
        return font.descriptor[pIndex][0]

    def _GetCharHeight(self, ch):
        """returns the height of a character, in pixels"""
        return font.fontInfo[0]

    def _GetStringWidth(self, st):
        """returns the width of the text, in pixels"""
        width = 0
        for ch in st:
            width += self._GetCharWidth(ch) + 1
        return width

    def _PutChar(self, ch, xPos, yPos, color=fColor):
        """Writes Ch to X,Y coordinates in current foreground color"""
        charData = self._GetCharData(ch)

        xLen = self._GetCharWidth(ch)  # char width, in pixels
        numRows = self._GetCharHeight(ch)

        bytesPerRow = 1 + ((xLen - 1) / 8)  # char width, in bytes
        numBytes = numRows * bytesPerRow

        self._SetAddrWindow(xPos, yPos, xPos + xLen - 1, yPos + numRows - 1)
        self._SetPin(self.DC, 0)
        self.spi.writebytes([self.RAMWR])  # pixel data to follow
        self._SetPin(self.DC, 1)
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
                            pixel = self.bColor  # 0: background color
                        else:
                            pixel = color  # 1: foreground color
                        buf.append(pixel >> 8)  # add pixel to buffer
                        buf.append(pixel & 0xFF)
                        mask >>= 1  # goto next bit in byte
                    bitNum += 1  # goto next bit in row
                index += 1  # goto next byte of data
        self.spi.writebytes(buf)  # send char data to TFT

    def PutString(self, xPos, yPos, st, color=fColor):
        """Draws string on display at xPos,yPos."
        "Does NOT check to see if it fits!"""
        for ch in st:
            width = self._GetCharWidth(ch) + 1
            self._PutChar(ch, xPos, yPos, color)
            xPos += width

    def CenterText(self, st, yPos, color=fColor):
        """Centers the text horizontally at given vertical position"""
        xPos = (self.XSIZE - self._GetStringWidth(st)) / 2
        self.PutString(xPos, yPos, st, color)

    #
    # font0
    #
    def _PutCh(self, ch, xPos, yPos, color=fColor):
        """write ch to X,Y coordinates using ASCII 5x7 font"""
        charData = font0.data[ord(ch) - 32]
        self._SetAddrWindow(xPos, yPos, xPos + 4, yPos + 6)
        self._SetPin(self.DC, 0)
        self.spi.writebytes([self.RAMWR])
        self._SetPin(self.DC, 1)
        buf = []
        mask = 0x01
        for row in range(7):
            for col in range(5):
                bit = charData[col] & mask
                if (bit == 0):
                    pixel = self.bColor
                else:
                    pixel = color
                buf.append(pixel >> 8)
                buf.append(pixel & 0xFF)
            mask <<= 1
        self.spi.writebytes(buf)

    def PutSt(self, st, x, y, c=fColor):
        """draws string using 5x7 font at pos x,y in color c"
        "Does NOT check to see if it fits!"""
        for ch in st:
            self._PutCh(ch, x, y, c)
            x += 6

    ########################################################################
    #
    # Testing routines:
    #
    #

    def PrintElapsedTime(self, function, startTime):
        """Formats an output string showing elapsed time since function start"""
        elapsedTime = time.time() - startTime
        logger.debug(u"%15s: %8.3f seconds" % (function, elapsedTime))
        time.sleep(1)

    def LabelIt(self, name):
        """write test name to screen"""
        self.ClearScreen()
        self.CenterText(name, 50)
        self.CenterText('Test', 70)
        time.sleep(1)
        self.ClearScreen()

    def ColorBars(self):
        """Fill Screen with 8 color bars"""
        for a in range(8):
            self.FillRect(0, a * 20, self.XMAX, a * 20 + 19, self.COLORSET[a + 1])

    def ScreenTest(self):
        """Measures time required to fill display twice"""
        self.LabelIt('Screen')
        startTime = time.time()
        self.FillScreen(self.LIME)
        self.FillScreen(self.MAGENTA)
        self.ColorBars()
        self.PrintElapsedTime('ScreenTest', startTime)

    def _RandRect(self):
        """Returns four integers x0,y0,x1,y1 as screen rect coordinates"""
        x1 = randint(1, 100)
        y1 = randint(1, 150)
        dx = randint(30, 80)
        dy = randint(30, 80)
        x2 = x1 + dx
        if x2 > 126:
            x2 = 126
        y2 = y1 + dy
        if y2 > 158:
            y2 = 158
        return x1, y1, x2, y2

    def _RandColor(self):
        """Returns a random color from BGR565 Colorspace"""
        index = randint(1, len(self.COLORSET) - 1)
        return self.COLORSET[index]

    def RectTest(self, numCycles=50):
        """Draws a series of random open rectangles"""
        self.ClearScreen()
        self.LabelIt('Rectangle')
        startTime = time.time()
        for a in range(numCycles):
            x0, y0, x1, y1 = self._RandRect()
            self.DrawRect(x0, y0, x1, y1, self._RandColor())
        self.PrintElapsedTime('RectTest', startTime)

    def FillRectTest(self, numCycles=70):
        """draws random filled rectangles on the display"""
        startTime = time.time()
        self.ClearScreen()
        for a in range(numCycles):
            x0, y0, x1, y1 = self._RandRect()
            self.FillRect(x0, y0, x1, y1, self._RandColor())
        self.PrintElapsedTime('FillRect', startTime)

    def LineTest(self, numCycles=50):
        """Draw a series of semi-random lines on display"""
        self.ClearScreen()
        self.LabelIt('Line')
        startTime = time.time()
        for a in range(numCycles):
            self.Line(10, 10, randint(20, 126), randint(20, 158), self.YELLOW)
            self.Line(120, 10, randint(2, 126), randint(10, 158), self.CYAN)
        self.PrintElapsedTime('LineTest', startTime)

    def PixelTest(self, color=BLACK, numPixels=5000):
        """Writes random pixels to the screen"""
        self.ClearScreen()
        self.LabelIt('Pixel')
        startTime = time.time()
        for i in range(numPixels):
            xPos = randint(0, self.XMAX)
            yPos = randint(0, self.YMAX)
            self.DrawPixel(xPos, yPos, self.LIME)
        self.PrintElapsedTime('PixelTest', startTime)

    def FastPixelTest(self, color=BLACK, numPixels=5000):
        """Writes random pixels to the screen"""
        self.ClearScreen()
        self.LabelIt('Pixel')
        startTime = time.time()
        for i in range(numPixels):
            xPos = randint(0, self.XMAX)
            yPos = randint(0, self.YMAX)
            self.SetPixel(xPos, yPos, self.YELLOW)
        self.PrintElapsedTime('FastPixelTest', startTime)

    def CircleMoireTest(self):
        """Draws a series of concentric circles"""
        self.ClearScreen()
        startTime = time.time()
        for radius in range(6, 60, 2):
            self.Circle(self.X0, self.Y0, radius, self.YELLOW)
        self.PrintElapsedTime('CircleMoire', startTime)

    def CircleTest(self, numCycles=20):
        """draw a series of random circles"""
        title = 'Circle'
        self.LabelIt(title)
        startTime = time.time()
        for a in range(numCycles):
            x = randint(30, 90)
            y = randint(30, 130)
            radius = randint(10, 40)
            self.Circle(x, y, radius, self._RandColor())
        self.PrintElapsedTime(title, startTime)

    def FastCircleTest(self, numCycles=20):
        """draw a series of random circles"""
        title = 'Fast Circle'
        self.LabelIt(title)
        startTime = time.time()
        for a in range(numCycles):
            x = randint(30, 90)
            y = randint(30, 130)
            radius = randint(10, 40)
            self.FastCircle(x, y, radius, self._RandColor())
        self.PrintElapsedTime(title, startTime)

    def FillCircleTest(self, numCycles=20):
        """draw a series of random filled circles"""
        self.ClearScreen()
        startTime = time.time()
        for a in range(numCycles):
            x = randint(30, 90)
            y = randint(30, 130)
            radius = randint(10, 40)
            self.FillCircle(x, y, radius, self._RandColor())
        self.PrintElapsedTime('FillCircleTest', startTime)

    def EllipseTest(self):
        title = 'Ellipse'
        self.LabelIt(title)
        startTime = time.time()
        for height in range(10, 150, 10):
            self.Ellipse(self.X0, self.Y0, 60, height, self.CYAN)
        for width in range(10, 120, 10):
            self.Ellipse(self.X0, self.Y0, width, 60, self.YELLOW)

        self.PrintElapsedTime(title, startTime)

    def FillEllipseTest(self):
        title = 'Fill Ellipse'
        startTime = time.time()
        for height in range(155, 10, -10):
            width = int(height * 0.8)
            self.FillEllipse(self.X0, self.Y0, width, height, self._RandColor())
        self.PrintElapsedTime(title, startTime)

    def VBarTest(self):
        title = 'VBar'
        self.LabelIt(title)
        startTime = time.time()
        data = [0, 0, 0, 0]
        for cycle in range(10):
            for col in range(4):
                xPos = 15 + 25 * col
                newValue = randint(30, 150)
                self.VBar(xPos, 150, 15, newValue, data[col], self.GREEN)
                data[col] = newValue
            time.sleep(1)
        self.PrintElapsedTime(title, startTime)

    def WaveTest(self):
        """similate wave motion with animated vertical bar graph"""
        title = 'Wave'
        self.LabelIt(title)
        startTime = time.time()
        data = [0, 0, 0, 0]
        for steps in range(40):
            for col in range(4):
                xPos = 15 + 25 * col
                if col == 3:
                    radians = 6.28 * (steps % 12) / 12
                    newValue = int(40 * sin(radians) + 70)
                else:
                    newValue = data[col + 1]
                self.VBar(xPos, 150, 15, newValue, data[col], self.CYAN)
                data[col] = newValue
            time.sleep(0.2)
        self.PrintElapsedTime(title, startTime)

    def SineTest(self):
        """draw a series of sin waves on screen"""
        title = 'Sine Graph'
        self.LabelIt(title)
        startTime = time.time()
        self.VLine(0, 0, 150, self.CYAN)
        self.HLine(0, 120, 75, self.CYAN)
        for step in range(0, 120, 10):
            for pixels in range(360):
                degrees = (pixels + step) % 360
                radians = 6.28 * degrees / 360.0
                val1 = sin(radians)
                val2 = cos(radians)
                x = int(pixels / 3)
                y1 = int(75 * val1 + 75)
                y2 = int(75 * val2 + 75)
                self.SetPixel(x, y1, self.YELLOW)
                self.SetPixel(x, y2, self.RED)
        self.PrintElapsedTime(title, startTime)
        time.sleep(1)

    def RunGraphicsTests(self):
        """run a series of graphics test routines & time them"""
        self.ScreenTest()  # fill entire screen with color
        self.RectTest(40)  # draw rectangles
        self.FillRectTest(25)  # draw filled rectangles
        self.FastPixelTest()  # draw 5000 random pixels
        self.CircleTest()  # draw random circles
        self.CircleMoireTest()  # draw concentric circles
        self.FillEllipseTest()  # draw filled ellipses
        self.WaveTest()  # draw animated wave
        self.SineTest()  # draw y=sin(x) graphs

    def PortaitChars(self):
        """Writes 420 characters (5x7) to screen in Portrait Mode"""
        # font is 5x7 with 1 pixel spacing
        # so character width = 6 pixels, height = 8 pixels
        # display width = 128 pixels, so 21 char per row (21x6 = 126)
        # display ht = 160 pixels, so 20 rows (20x8 = 160)
        # total number of characters = 21 x 20 = 420

        CHARS_PER_ROW = 21
        self.FillRect(0, 0, self.XMAX, self.YMAX, self.bColor)  # clear screen
        for i in range(420):
            x = i % CHARS_PER_ROW
            y = i / CHARS_PER_ROW
            ascii = (i % 96) + 32
            self._PutCh(chr(ascii), x * 6, y * 8)
        time.sleep(1)

    def LandscapeChars(self):
        """Writes 416 characters (5x7) to screen, landscape mode"""
        # font is 5x7 with 1 pixel spacing
        # so character width = 6 pixels, height = 8 pixels
        # display width = 160 pixels, so 26 char per row (26x6 = 156)
        # display ht = 128 pixels, so 16 rows (16x8 = 128)
        # total number of characters = 26 x 16 = 416
        CHARS_PER_ROW = 26
        self.FillRect(0, 0, self.YMAX, self.XMAX, self.bColor)  # clear screen
        for i in range(416):
            x = i % CHARS_PER_ROW
            y = i / CHARS_PER_ROW
            ascii = (i % 96) + 32
            self._PutCh(chr(ascii), x * 6, y * 8, self.CYAN)
        time.sleep(1)

    def LargeFontTest(self):
        """Writes 90 characters (11x17) to the screen"""
        title = 'Large Font'
        self.LabelIt(title)

        startTime = time.time()
        for i in range(90):
            x = i % 10
            y = i / 10
            ascii = (i % 96) + 32
            self._PutChar(chr(ascii), x * 12, y * 18, self.LIME)

        self.PrintElapsedTime(title, startTime)

    def SmallFontTest(self):
        """Writes 1000 random 5x7 characters to the screen"""
        title = 'Small Font'
        self.LabelIt(title)

        startTime = time.time()
        for i in range(1000):
            x = randint(0, 20)
            y = randint(0, 19)
            color = self._RandColor()
            ascii = (i % 96) + 32
            self._PutCh(chr(ascii), x * 6, y * 8, color)

        self.PrintElapsedTime(title, startTime)

    def OrientationTest(self):
        """Write 5x7 characters at 0,90,180,270 deg orientations"""
        title = 'Orientation'
        startTime = time.time()
        self.LabelIt(title)
        self.PortaitChars()
        self.SetOrientation(90)  # display-top on right
        self.LandscapeChars()
        self.SetOrientation(180)  # upside-down
        self.PortaitChars()
        self.SetOrientation(270)  # display-top on left
        self.LandscapeChars()
        self.SetOrientation(0)  # return to 0 deg.
        self.PrintElapsedTime(title, startTime)

    def _GetTempCPU(self):
        """Returns CPU temp in degrees F"""
        tPath = '/sys/class/thermal/thermal_zone0/temp'
        tFile = open(tPath)
        temp = tFile.read()
        tFile.close()
        return (float(temp) * 0.0018 + 32)

    def _Run(self, cmd):
        """Runs a system (bash) command"""
        return os.popen(cmd).read()

    def _GetIPAddr(self):
        """Returns IP address as a string"""
        cmd = "ifconfig | awk '/192/ {print $2}'"
        res = self._Run(cmd).replace('addr:', '')
        return res.replace('\n', '')

    def InfoTest(self):
        """Show Time on screen"""
        title = 'Info'
        self.LabelIt(title)
        startTime = time.time()  # keep track of test duration
        self.PutString(0, 0, 'IP addr', self.WHITE)
        self.PutString(0, 20, self._GetIPAddr())
        self.PutString(0, 60, 'CPU temp', self.WHITE)
        temp = self._GetTempCPU()
        self.PutString(0, 80, '{:5.1f} deg F'.format(temp))
        tStr = time.strftime("%I:%M:%S ")
        self.PutString(0, 120, 'Time', self.WHITE)
        self.PutString(0, 140, tStr)
        self.PrintElapsedTime(title, startTime)

    def RunTextTests(self):
        self.LargeFontTest()
        self.SmallFontTest()
        self.OrientationTest()
        self.InfoTest()

    ########################################################################
    #
    # Color routines:
    #
    #

    def _PackColor(self, red, green, blue):
        """Packs individual red,green,blue color components into 16bit color"
        "16-bit color format is rrrrrggg.gggbbbbb"
        "Max values: Red 31, Green 63, Blue 31"""
        r = red & 0x1F
        g = green & 0x3F
        b = blue & 0x1F
        return (r << 11) + (g << 5) + b

    def _UnpackColor(self, color):
        """Reduces 16-bit color into component r,g,b values"""
        r = color >> 11
        g = (color & 0x07E0) >> 5
        b = color & 0x001F
        return r, g, b

    def _Brightness(self, color):
        """returns brightness of color pixel: 0=black,99=white"""
        r, g, b = self._UnpackColor(color)
        return int(0.94 * r + 0.94 * g + 0.31 * b)

    def Complement(self, color):
        """Returns color complement"""
        r, g, b = self._UnpackColor(color)
        return self._PackColor(31 - r, 63 - g, 31 - b)

    def TriadColors(self, color):
        """Returns two triad colors for given color"""
        r, g, b = self._UnpackColor(color)
        tr1 = self._PackColor(b, r * 2, g / 2)  # rgb --> brg
        tr2 = self._PackColor(g / 2, b * 2, r)  # rgb --> gbr
        return tr1, tr2

    def TriadDisplay(self, c1):
        """Displays color triad & their compliments"""
        c2, c3 = self.TriadColors(c1)
        comp1 = self.Complement(c1)
        comp2 = self.Complement(c2)
        comp3 = self.Complement(c3)
        dy = 40
        self.FillRect(1, 0 + dy, 42, 41 + dy, c2)
        # FillRect(43,0+dy,84,41+dy,c1)
        self.FillRect(85, 0 + dy, 126, 41 + dy, c3)
        self.FillRect(1, 42 + dy, 42, 83 + dy, comp2)
        self.FillRect(43, 42 + dy, 84, 83 + dy, comp1)
        self.FillRect(85, 42 + dy, 126, 83 + dy, comp3)

    def ColorDictionary(self, filename):
        """'loads color dictionary from a file'"""
        # the file contains a list of named colors, one per line
        # each line is of the format COLORNAME = 0xFFFF
        d = {}
        for line in open(filename):  # scan each line of file
            if line.find('=') > 0:  # ignore lines without '='
                words = line.split('=')  # split line into two words
                key = words[0].strip()  # first word is the key (colorname)
                value = words[1].strip()  # second word is the RGB value
                try:
                    d[key] = int(value, 16)  # add pair to dictionary, converting to hex
                except Exception, msg:
                    logger.debug("%s" % msg)

        return d

    def ColorInputTest(self):
        """'Ask user of R,G,B compononents (0-255); Display color on screen'
        'To quit, enter value of >255 for red'"""
        self.ClearScreen()
        while True:
            r = eval(raw_input('red? '))
            if r > 255:
                break
            g = eval(raw_input('green? '))
            b = eval(raw_input('blue? '))
            r >>= 3
            g >>= 2
            b >>= 3
            color = self._PackColor(r, g, b)
            self.FillRect(0, 0, 127, 128, color)
            st = "({0:2d},{1:2d},{2:2d}) = {3:4x} ".format(r, g, b, color)
            self._PutSt(st, 10, 140, self.WHITE)

    def ColorTest(self, filename='/home/pi/tft/rgb565.py'):
        """Loads a color dictionary; displays sample colors w/ complements"""
        # self.bColor
        self.LabelIt('Color')

        # load a dictionary with all of the color names & RGB values
        dictionary = self.ColorDictionary(filename)

        # demo with just a few colors
        colorNames = ['AQUA', 'ORANGE', 'MAGENTA', 'SKYBLUE', 'TOMATO', 'NAVY']

        for name in colorNames:
            color = dictionary[name]

            CUTOFF = 65  # 65 for gamma corrected, 30 for uncorrected
            self.bColor = color

            # display color and it's name
            self.FillRect(0, 0, self.XSIZE, self.XSIZE, color)  # set background to color

            length = len(name)
            while self._GetStringWidth(name[0:length]) > self.XSIZE:
                length -= 1
            abbrev = name[0:length]  # trunc name to fit on screen
            b = self._Brightness(color)  # get brightness of this color
            if self._Brightness(color) < CUTOFF:
                c1 = self.WHITE  # dark colors get white text
            else:
                c1 = self.BLACK  # light colors get dark text
            self.CenterText(abbrev, 20, c1)  # display color name
            self.CenterText(str(b), 40, c1)  # display brightness
            self.bColor = self.BLACK  # restore background color

            # display RGB component information at bottom of display
            r, g, b = self._UnpackColor(color)
            st = "({0:2d},{1:2d},{2:2d}) = {3:4x} ".format(r, g, b, color)
            self._PutSt(st, 10, 140, self.WHITE)
            st = "{:20s}".format(name)
            self._PutSt(st, 10, 150, self.WHITE)
            time.sleep(1)

            # display triad colors & their complements
            self.TriadDisplay(color)
            time.sleep(1)

    ########################################################################
    #
    # BMP Routines - Read .bmp Graphics File Format
    #

    def DrawBMP(self, fileName, displayHeader=False):
        INT4 = '<l'  # get 4-byte word from unpacking routine
        INT2 = '<h'  # get 2-byte word from unpacking routine

        self.ClearScreen()

        # read entire file into list variable 'data'
        data = open(fileName, 'rb').read()

        signature = data[0:2]
        if signature != 'BM':
            logger.debug('Not a bitmap file')
            return
        else:
            pass

        # Get information from BMP header
        fileSize = unpack_from(INT4, data, 02)[0]
        offset = unpack_from(INT4, data, 10)[0]
        width = unpack_from(INT4, data, 18)[0]
        height = unpack_from(INT4, data, 22)[0]
        numPlanes = unpack_from(INT2, data, 26)[0]
        colorBits = unpack_from(INT2, data, 28)[0]
        compType = unpack_from(INT4, data, 30)[0]
        imageSize = unpack_from(INT4, data, 34)[0]
        horizRes = unpack_from(INT4, data, 38)[0]
        vertRes = unpack_from(INT4, data, 42)[0]

        # optionally display header information
        if displayHeader:
            logger.debug('Filename ', fileName)
            logger.debug('Signature ', signature)
            logger.debug('File Size ', fileSize)
            logger.debug('Offset ', offset)
            logger.debug('Width ', width)
            logger.debug('Height ', height)
            logger.debug('Planes ', numPlanes)
            logger.debug('ColorBits ', colorBits)
            logger.debug('Compression ', compType)
            logger.debug('ImageSize ', imageSize)
            logger.debug('Horiz Res ', horizRes)
            logger.debug('Vert Res ', vertRes)

        if (numPlanes != 1) or (colorBits != 24) or (compType != 0):
            logger.debug('Unsupported BMP format')
            return

        rowSize = (width * 3 + 3) & ~3

        # send pixel data from file to TFT
        self._SetAddrWindow(0, 0, width - 1, height - 1)
        self._SetPin(self.DC, 0)
        self.spi.writebytes([self.RAMWR])  # pixel data to follow
        self._SetPin(self.DC, 1)

        for row in range(height):  # do one row at a time
            buf = []  # buffer for row of pixels
            index = (height - row - 1) * rowSize + offset

            for col in range(width):  # for each pixel in this row:
                b = ord(data[index])  # get blue subpixel (0-255)
                g = ord(data[index + 1])  # get green subpixel (0-255)
                r = ord(data[index + 2])  # get red subpixel (0-255)
                pixel = self._PackColor(r >> 3, g >> 2, b >> 3)  # pack into RGB565 format
                buf.append(pixel >> 8)  # add pixel to buffer (MSB, LSB)
                buf.append(pixel & 0xFF)
                index += 3  # go to next pixel in data stream

            self.spi.writebytes(buf)  # send row of pixel data to TFT

    ########################################################################
    #
    # Gamma routines:
    #
    #

    def SetGamma(self):
        """'Sets Gamma table with manufacturer recommended values'"""
        'These values are very close to a Gamma of 2.2'
        self._Command(self.GAMCTP, 0x02, 0x1C, 0x07, 0x12, 0x37, 0x32, 0x29, 0x2D,
                      0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10)
        self._Command(self.GAMCTN, 0x03, 0x1D, 0x07, 0x06, 0x2E, 0x2C, 0x29, 0x2D,
                      0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10)

    def GamSet(self, value, text):
        """'Set gamma & show text label at bottom of screen'
        'Called by CycleGammas routine'"""
        self.FillRect(0, 150, 127, 159, self.BLACK)
        self._PutSt(text, 20, 152, self.WHITE)
        self._Command(self.GAMSET, value)
        time.sleep(2)

    def CycleGammas(self, numCycles=3):
        """'Cycle display through four different gamma settings'"""
        for count in range(numCycles):
            self.GamSet(1, 'Gamma 1.0')
            self.GamSet(2, 'Gamma 2.5')
            self.GamSet(4, 'Gamma 2.2')
            self.GamSet(8, 'Gamma 1.8')

    def GradientFill(self):
        """Draw a vertical color gradient fill on TFT, bright to dark green"""
        self.ClearScreen()
        for i in range(64):
            self.FillRect(0, 2 * i, 127, 2 * i + 1, self._PackColor(0, 63 - i, 0))
        self.DrawRect(0, 0, 127, 128, self.GREEN)

    def BandedFill(self):
        """Draws Black-to-white bars, left to right, in 10 equal steps"""
        self.ClearScreen()
        for i in range(10):
            self.FillRect(12 * i, 0, 12 * i + 11, 128, self._PackColor(i * 3, i * 6, i * 3))
        self.DrawRect(0, 0, 120, 128, self.GRAY)

        # this test shows that GamSet sets up the gamma table to reflect
        # the desired gamma value. If you set your gamma table then call
        # GamSet, your table is wiped out. If you call GamSet then set your
        # values, the GamSet is wiped out. There is only one table; not
        # four separate tables for each gamma setting.
        # Adafruits gamma settings is very close to Gamset(2).

    def RunGammaTests(self):
        """Display gradients & images with different gamma curves"""
        self.ClearScreen()
        self.LabelIt('Gamma')

        self.BandedFill()
        self.CycleGammas(1)
        self.GradientFill()
        self.CycleGammas(1)
        self.DrawBMP('parrot.bmp')
        self.CycleGammas(1)
        time.sleep(1)


#
# Main Program
#
if __name__ == u"__main__":
    logger.debug("Adafruit 1.8 TFT display demo with hardware SPI")

    libtft = TFTLib()

    libtft.ClearScreen()

    libtft.RunTextTests()  # run suite of text tests

    libtft.RunGraphicsTests()  # run suite of graphic tests

    libtft.ColorTest()  # display named colors & complements

    libtft.RunGammaTests()  # run suite of gamma tests

    libtft.DrawBMP("/home/pi/tft/parrot.bmp", displayHeader=True)

    time.sleep(10)

    libtft.spi.close()  # close down SPI interface

    logger.debug("Done.")
