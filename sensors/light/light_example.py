#!/usr/bin/env python
import os
import sys
import tsl2591

tsl = tsl2591.Tsl2591()  # initialize
full, ir = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
lux = tsl.calculate_lux(full, ir)  # convert raw values to lux
print("lux=%3.2f\tfull=%3.2f\tir=%3.2f" % (lux, full, ir))

