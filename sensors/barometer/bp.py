#!/usr/bin/env python
__author__ = u"james.morris"

if __name__ == u"__main__":

    debug = True

    # Read registers --> these are the values in the example from the MPL115A2 Data Sheet page 9
    Padc_tmp = 0x6680
    Tadc_tmp = 0x7EC0
    a0_temp = 0x3ECE
    b1_temp = 0xB3F9
    b2_temp = 0xC517
    c12_temp = 0x33C8

    # Getting Padc --> only 10 bits all integer, so shift all to right by 6
    Padc = Padc_tmp >> 6
    if debug:
        print "Padc: %04i ADC" % (Padc), " expected 410 ADC"

    # Getting Tadc --> only 10 bits all integer, so shift all to right by 6
    Tadc = Tadc_tmp >> 6
    if debug:
        print "Tadc: %04i ADC" % (Tadc), " expected 507 ADC"

    # Calulate a0 p6 in the documentation
    a0_signed = a0_temp >> 15  # check for signed bit in 16th bit possition
    if a0_signed:
        a0_temp = a0_temp - 0x8000  # remove sign bit
        a0 = float(~a0_temp) / 0x8  # add python sign, create float and move dec. 3 bits in
    else:
        a0 = float(a0_temp) / 0x8  # create float and move dec. 3 bits in
    if debug:
        print "a0: ", a0, " expected 2009.75"

    # Calculate b1 p6 in the documentation
    b1_signed = (b1_temp & 0x8000) >> 15
    if b1_signed:
        b1_temp = b1_temp - 0x8000
        b1 = float(~b1_temp) / 0x2000
    else:
        b1 = float(b1_temp) / 0x2000  # move dec. to left 12 places
    if debug:
        print "b1: ", b1, " expected -2.37585"
        # b1 = -2.37585

    # Calculate b2 p6 in the documentation
    b2_signed = (b2_temp & 0x8000) >> 15
    if b2_signed:
        b2_temp = b2_temp - 0x8000
        b2 = float(~b2_temp) / 0x4000
    else:
        b2 = float(b2_temp) / 0x4000  # move dec. to left 13 places
    if debug:
        print "b2: ", b2, " expected -0.92047"
        # b2 = -0.92047

    # Calculate c12 p6 in the documentation
    c12_signed = (c12_temp & 0x8000) >> 15
    if c12_signed:
        c12_temp = c12_temp - 0x8000
        c12_temp = c12_temp >> 2  # nip off the last two not used bits by shifting to the right
        c12 = float(~c12_temp) / 0x400000
    else:
        c12_temp = c12_temp >> 2  # nip off the last two not used bits by shifting to the right
        c12 = float(c12_temp) / 0x400000  # move dec. to left (12+9) places
    if debug:
        print "c12: ", c12, "expected 0.000790"

    Pcomp = a0 + (b1 + c12 * Tadc) * Padc + b2 * Tadc
    if debug:
        print "Pcomp: ", Pcomp, " expected 733.19051"

    Tcomp = ((Tadc - 498.0) / -5.35 + 25.0)
    Pcomp = ((Pcomp * ((115.0 - 50.0) / 1023.0)) + 50.0)
    Lreturn = [Pcomp, Tcomp]
    print Lreturn
