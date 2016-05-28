#!/usr/bin/env python
from BrickPi import *

BrickPiSetup()
BrickPi.SensorType[PORT_4] = TYPE_SENSOR_ULTRASONIC_CONT
BrickPiSetupSensors()

if __name__ == "__main__":
    while True:
        result = BrickPiUpdateValues()
        if not result:
            value = BrickPi.Sensor[PORT_4] * 2 
            print("%d" % value)

        time.sleep(.01)

