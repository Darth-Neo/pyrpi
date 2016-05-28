#!/usr/bin/env python
from BrickPi import *

SENSOR_ACCEL = TYPE_SENSOR_ULTRASONIC_CONT

BrickPiSetup()
BrickPi.SensorType[PORT_3] = SENSOR_ACCEL 
BrickPiSetupSensors()

if __name__ == "__main__":
    while True:
        result = BrickPiUpdateValues()
        if not result:
            value = BrickPi.Sensor[PORT_3] 
            print("\r%d" % value)

        time.sleep(.01)

