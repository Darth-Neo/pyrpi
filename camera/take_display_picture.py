#!/usr/bin/env python

#
# Pi Camera Example Photo
#
import os
import time
import picamera
import pygame, sys
import time
from pygame.locals import *

# set window size to match picture size
width = 640
height = 480
    
def displayPicture(picture, sleep=2):
    # initialise pygame
    pygame.init()
    
    screen = pygame.display.set_mode((width,height),1,16)
    
    #load picture
    background= pygame.image.load(picture)

    # display picture
    screen.blit(background,(0,0))

    pygame.display.flip()
    

def takePicture(file):
  global width
  global height
  
  with picamera.PiCamera() as camera:
    # camera.resolution = (width, height)
    
    camera.hflip = True
    camera.vflip = True

    camera.capture(file)

if __name__ == '__main__':

    if False:
      path = "/home/pi/picture"
      os.chdir(path)
      file = "image_" + time.strftime(u"%Y%d%m_%H%M%S") + ".bmp"
      
      takePicture(file)
      print("Image stored at %s%s%s" % (path, os.sep, file))
	
    else:
      file = "image.bmp"
      sleep = 0.5
      
      while True:
	try:
	  takePicture(file)
	  displayPicture(file)
	  time.sleep(sleep)
	
	except KeyboardInterrupt, msg:
	  print("Goodbye : %s" % msg)
	  break

