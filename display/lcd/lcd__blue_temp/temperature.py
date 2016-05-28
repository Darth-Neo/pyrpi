#!/usr/bin/env python
import sys

import Adafruit_DHT
from time import gmtime, strftime
import datetime

if __name__ == "__main__":
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    # '2009-01-05 22:14:39'

    # Parse command line parameters.
    sensor_args = {'11': Adafruit_DHT.DHT11,
                   '22': Adafruit_DHT.DHT22,
                   '2302': Adafruit_DHT.AM2302}

    if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
        sensor = sensor_args[sys.argv[1]]
        pin = sys.argv[2]
    else:
        sensor = Adafruit_DHT.AM2302
        pin = '4'
    # print 'usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#'
    # print 'example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4'
    # sys.exit(1)

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    if humidity is not None and temperature is not None:
        f = temperature * (9.0 / 5.0) + 32
        print("%s\tTemp=%3.2f*C\t Temp=%3.2f*f\tHumidity=%0.2f%%" % (dt, temperature, f, humidity))
    # print("Temp=%3.2f*f\t Humidity=%0.2f%%" % (f, humidity))
    else:
        print 'Failed to get reading. Try again!'

    dt = datetime.now().strftime('%I:%M')
    hour = int(dt.split(":")[0])
    minute = int(dt.split(":")[1])

    if minute == 0 or minute == 15 or minute == 30 or minute == 45:
        lcd.set_backlight(1)
        sleep(30)
        lcd.set_backlight(0)
