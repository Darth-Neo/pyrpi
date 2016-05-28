#!/usr/bin/env python
import RPi.GPIO as GPIO
import collections, signal, sys
from time import sleep

# get command line agruments
arg_names = ['command', 'direction']
args      = dict(zip(arg_names, sys.argv))
arg_list  = collections.namedtuple('arg_list', arg_names)
args      = arg_list(*(args.get(arg, None) for arg in arg_names))

# set initial values
step      = 1
mota      = 18
motb      = 17
left      = motb
right     = mota
reps      = 400
hertz     = 2000
freq      = (1 / float(hertz)) - 0.0003
ports     = [mota,motb]
percent   = 100

# function to run the motor
def run_motor(reps, pulse_width, port_num, period):
    for i in range(0, reps):
        GPIO.output(port_num, True)
        sleep(pulse_width)
        GPIO.output(port_num, False)
        sleep(period)

# trap SIGINT and provide a clean exit path
def signal_handler(signal, frame):
    GPIO.output(direction, False)
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

GPIO.setmode(GPIO.BCM)

# initialize the ports being used
for port_num in ports:
    GPIO.setup(port_num, GPIO.OUT)
    print "setting up GPIO port:", port_num
    GPIO.output(port_num, False)

# determine direction or set a default
if args[1] == "left":
    direction = left
elif args[1] == "right":
    direction = right
else:
    direction = right

# the main loop
while True:
    pulse_width = percent / float(100) * freq
    period      = freq - (freq * percent / float(100))
    run_motor(reps, pulse_width, direction, period)