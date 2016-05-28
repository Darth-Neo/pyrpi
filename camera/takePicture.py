#!/usr/bin/python
#
# Pi Camera Example Photo
#
import os
import time
import picamera

def takePicture(file):

  with picamera.PiCamera() as camera:
    # camera.resolution = (128, 160)
    
    camera.hflip = True
    camera.vflip = True

    camera.capture(file)

if __name__ == '__main__':

    path = "/home/pi/picture"
    os.chdir(path)
    file = "image_" + time.strftime(u"%Y%d%m_%H%M%S") + ".bmp"
    
    takePicture(file)
    
    print("Image stored at %s%s%s" % (path, os.sep, file))

