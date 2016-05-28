#!/usr/bin/env python
# __author__ = u"james.morris"
import time
from Adafruit_I2C import Adafruit_I2C


class MPL115A2(object):
    i2c = None

    # Registers
    __MPL115A2_Padc_MSB = 0x00
    __MPL115A2_Padc_LSB = 0x01
    __MPL115A2_Tadc_MSB = 0x02
    __MPL115A2_Tadc_LSB = 0x03
    __MPL115A2_a0_MSB = 0x04
    __MPL115A2_a0_LSB = 0x05
    __MPL115A2_b1_MSB = 0x06
    __MPL115A2_b1_LSB = 0x07
    __MPL115A2_b2_MSB = 0x08
    __MPL115A2_b2_LSB = 0x09
    __MPL115A2_c12_MSB = 0x0A
    __MPL115A2_c12_LSB = 0x0B
    __MPL115A2_CONVERT = 0x12

    def __init__(self, address=0x60, debug=False):
        self.i2c = Adafruit_I2C(address)
        self.debug = debug

    def getPT(self):
        # Start conversion
        self.i2c.write8(self.__MPL115A2_CONVERT, 0)

        # Wait for conversion to complete
        time.sleep(0.003)

        # Read registers
        self.Padc_tmp = (self.i2c.readU8(self.__MPL115A2_Padc_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_Padc_LSB)
        self.Tadc_tmp = (self.i2c.readU8(self.__MPL115A2_Tadc_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_Tadc_LSB)
        self.a0_temp = (self.i2c.readU8(self.__MPL115A2_a0_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_a0_LSB)
        self.b1_temp = (self.i2c.readU8(self.__MPL115A2_b1_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_b1_LSB)
        self.b2_temp = (self.i2c.readU8(self.__MPL115A2_b2_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_b2_LSB)
        self.c12_temp = (self.i2c.readU8(self.__MPL115A2_c12_MSB) << 8) + self.i2c.readU8(self.__MPL115A2_c12_LSB)

        # Getting Padc
        self.Padc = (self.Padc_tmp & 0xFFC0) >> 6
        if self.debug:
            print("Padc: %04i (0x%04X)" % (self.Padc, self.Padc))

        # Getting Tadc
        self.Tadc = (self.Tadc_tmp & 0xFFC0) >> 6
        if self.debug:
            print("Tadc: %04i (0x%04X)" % (self.Tadc, self.Tadc))

        # Calulate a0 p6 in the documentation
        self.a0_signed = (self.a0_temp & 0x8000) >> 15
        self.a0_main = (self.a0_temp & 0x7FF8) >> 3
        self.a0_fraction = (self.a0_temp & 0x0007)
        self.a0 = float(str(self.a0_main) + "." + str(self.a0_fraction))
        if self.a0_signed:
            self.a0_temp = ~self.a0_temp
            self.a0_main = (self.a0_temp & 0x7FF8) >> 3
            self.a0_fraction = (self.a0_temp & 0x0007)
            self.a0 = float(str(self.a0_main) + "." + str(self.a0_fraction))
            self.a0 = -self.a0
        else:
            self.a0_main = (self.a0_temp & 0x7FF8) >> 3
            self.a0_fraction = (self.a0_temp & 0x0007)
            self.a0 = float(str(self.a0_main) + "." + str(self.a0_fraction))
        if self.debug:
            print("a0: %3.3f" %  self.a0)

        # Calculate b1 p6 in the documentation
        self.b1_signed = (self.b1_temp & 0x8000) >> 15
        if self.b1_signed:
            self.b1_temp = ~self.b1_temp
            self.b1_main = (self.b1_temp & 0x6000) >> 13
            self.b1_fraction = (self.b1_temp & 0x1FFF)
            self.b1 = float(str(self.b1_main) + "." + str(self.b1_fraction))
            self.b1 = -self.b1
        else:
            self.b1_main = (self.b1_temp & 0x6000) >> 13
            self.b1_fraction = (self.b1_temp & 0x1FFF)
            self.b1 = float(str(self.b1_main) + "." + str(self.b1_fraction))
        if self.debug:
            print("b1: %3.3f" % self.b1)

        # Calculate b2 p6 in the documentation
        self.b2_signed = (self.b2_temp & 0x8000) >> 15
        if self.b2_signed:
            self.b2_temp = ~self.b2_temp
            self.b2_main = (self.b2_temp & 0x4000) >> 14
            self.b2_fraction = (self.b2_temp & 0x3FFF)
            self.b2 = float(str(self.b2_main) + "." + str(self.b2_fraction))
            self.b2 = -self.b2
        else:
            self.b2_main = (self.b2_temp & 0x4000) >> 14
            self.b2_fraction = (self.b2_temp & 0x3FFF)
            self.b2 = float(str(self.b2_main) + "." + str(self.b2_fraction))

        if self.debug:
            print("b2: %3.3f" % self.b2)

        # Calculate c12 p6 in the documentation
        self.c12_signed = (self.c12_temp & 0x8000) >> 15
        if self.c12_signed:
            self.c12_temp = ~self.c12_temp
            self.c12_signed = (self.c12_temp & 0x8000) >> 15
            self.c12_fraction = (self.c12_temp & 0x7FFC) >> 2
            self.c12 = float("0." + "%09d" % self.c12_fraction)
            self.c12 = -self.c12
        else:
            self.c12_signed = (self.c12_temp & 0x8000) >> 15
            self.c12_fraction = (self.c12_temp & 0x7FFC) >> 2
            self.c12 = float("0." + "%09d" % self.c12_fraction)
        if self.debug:
            print("c12: %3.3f" % self.c12)

        self.Pcomp = self.a0 + (self.b1 + self.c12 * self.Tadc) * self.Padc + self.b2 * self.Tadc

        if self.debug:
            print("Pcomp: %3.3f" % self.Pcomp)

        self.Tcomp = ((self.Tadc - 498.0) / -5.35 + 25.0)
        self.Pcomp = ((self.Pcomp * ((115.0 - 50.0) / 1023.0)) + 50.0)
        self.Lreturn = [self.Pcomp, self.Tcomp]
        return self.Lreturn


if __name__ == u"__main__":
    mpl = MPL115A2(address=0x60, debug=True)
    mpl.getPT()

