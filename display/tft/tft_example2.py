#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import spidev  # hardware SPI

# TFT to RPi connections
# PIN TFT RPi
#  1 backlight 3V3
#  2 MISO <none>
#  3 CLK SCLK (GPIO 11)
#  4 MOSI MOSI (GPIO 10)
#  5 CS-TFT GND
#  6 CS-CARD <none>
#  7 D/C GPIO GPIO24
#  8 RESET GPIO25
#  9 VCC 3V3
#  10 GND GND

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

COLORSET = [BLACK, BLUE, RED, GREEN, LIME, CYAN, MAGENTA, YELLOW, WHITE, PURPLE,
            NAVY, TEAL, OLIVE, MAROON, SILVER, GRAY]

# ST7735 commands
SWRESET = 0x01  # software reset
SLPOUT  = 0x11  # sleep out
DISPON  = 0x29  # display on
CASET   = 0x2A  # column address set
RASET   = 0x2B  # row address set
RAMWR   = 0x2C  # RAM write
MADCTL  = 0x36  # axis control
COLMOD  = 0x3A  # color mode

#
# Low-level routines
# These routines access GPIO directly
#


def SetPin(pinNumber, value):
    # sets the GPIO pin to desired value (1=on,0=off)
    GPIO.output(pinNumber, value)


def InitIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(DC, GPIO.OUT)
    GPIO.setup(RST, GPIO.OUT)
    GPIO.output(RST, GPIO.LOW)
    GPIO.output(RST, GPIO.HIGH)

#
# Hardware SPI routines:
#


def WriteByte(value, data=True):
    SetPin(DC, data)
    spi.writebytes([value])


def WriteCmd(value):
    """Send command byte to display"""
    WriteByte(value, False)  # set D/C line to 0 = command


def WriteWord(value):
    """sends a 16-bit word to the display as data"""
    WriteByte(value >> 8)  # write upper 8 bits
    WriteByte(value & 0xFF)  # write lower 8 bits


def WriteList(byteList):
    """Send list of bytes to display, as data"""
    for byte in byteList:  # grab each byte in list
        WriteByte(byte)  # and send it


def Write888(value, width, count):
    """sends a 24-bit RGB pixel data to display, with optional repeat"""
    red = value >> 16  # red = upper 8 bits
    green = (value >> 8) & 0xFF  # green = middle 8 bits
    blue = value & 0xFF  # blue = lower 8 bits
    RGB = [red, green, blue]  # assemble RGB as 3 byte list
    SetPin(DC, GPIO.HIGH)
    for a in range(count):
        spi.writebytes(RGB * width)


#
# ST7735 driver routines:
#

def InitDisplay():
    """Resets & prepares display for active use."""

    WriteCmd(SWRESET)  # software reset, puts display into sleep
    time.sleep(0.2)  # wait 200mS for controller register init

    WriteCmd(SLPOUT)  # sleep out
    time.sleep(0.2)  # wait 200mS for TFT driver circuits

    WriteCmd(DISPON)  # display on!


def SetAddrWindow(x0, y0, x1, y1):
    """sets a rectangular display window into which pixel data is placed"""
    WriteCmd(CASET)  # set column range (x0,x1)
    WriteWord(x0)
    WriteWord(x1)
    WriteCmd(RASET)  # set row range (y0,y1)
    WriteWord(y0)
    WriteWord(y1)


def FillRect(x0, y0, x1, y1, color):
    """fills rectangle with given color"""
    width = x1 - x0 + 1
    height = y1 - y0 + 1
    SetAddrWindow(x0, y0, x1, y1)
    WriteCmd(RAMWR)
    Write888(color, width, height)


def FillScreen(color):
    """Fills entire screen with given color"""
    FillRect(0, 0, 127, 159, color)


def ClearScreen():
    """Fills entire screen with black"""
    FillRect(0, 0, 127, 159, BLACK)


#
# Testing routines:
#

def TimeDisplay():
    """Measures time required to fill display twice"""
    startTime = time.time()
    for x in COLORSET:
        FillScreen(x)
    ClearScreen()
    elapsedTime = time.time() - startTime
    print(" Elapsed time %0.1f seconds" % (elapsedTime))


if __name__ == u"__main__":
    print("Adafruit 1.8 TFT display demo with hardware SPI")
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.mode = 0

    InitIO()

    InitDisplay()
    TimeDisplay()
    spi.close()
    print("Done.")
