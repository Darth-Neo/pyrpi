#! /
usr/bin/env python
import time
import picamera

if __name__ == u'__main__':
    
  with picamera.PiCamera() as camera:
    camera.resolution = (159, 127)
    
    camera.start_preview()
    time.sleep(10)
    camera.capture('foo.bmp')
    
    camera.stop_preview()
    