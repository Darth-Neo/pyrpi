#!/usr/bin/env python

import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_recording('1.h264')
    camera.wait_recording(5)
    for i in range(2, 11):
        camera.split_recording('%d.h264' % i)
        camera.wait_recording(5)
    camera.stop_recording()
