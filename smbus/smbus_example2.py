#!/usr/bin/env python
import smbus

# As before, we'll create an alias for our addresses, just to make things
# a bit easier and more readable later on.
gyroAddress = 0x48
xlAddress   = 0x42

# Initialize an smbus object. The parameter passed is the number of the I2C
#   bus; for the Arduino-ish headers on the pcDuino, it will be "2".
bus = smbus.SMBus(1)

# With both of these devices, the first byte written specifies the address of
#   the register we want to read or write; for both devices, the device ID is
#   stored in location 0. Writing that address, than issuing a read, will
#   give us our answer.
result = bus.write_byte(gyroAddress, 0)
print("%d - Device ID: %s " % (result, str(bus.read_byte(gyroAddress))) ## should be 105

