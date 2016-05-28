#!/usr/bin/env python
__author__ = u"james.morris"
import smbus
import time

def write_i2c_block(address, block):
    try:
            return bus.write_i2c_block_data(address, 1, block)
    except IOError:
            print(u"IOError")
            return -1

def analogRead(pin):
        bus.write_i2c_block_data(address, 1, aRead_cmd + [pin, unused, unused])
        time.sleep(.1)
        bus.read_byte(address)
        number = bus.read_i2c_block_data(address, 1)
        return number[1] * 256 + number[2]

if __name__ == u"__main__":
    address = 0x29

    #Code used from GrovePi.py for testing.
    pMode_cmd = [5]
    aRead_cmd = [3]
    bus = smbus.SMBus(1)
    unused = 0

    write_i2c_block(address, pMode_cmd + [1, unused, unused])

    print analogRead(0)