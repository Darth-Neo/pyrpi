#!/usr/bin/env python

import os
import pygame, sys
import time
from pygame.locals import *

if __name__ == u"__main__":
    # set window size to match picture size
    width = 640
    height = 480

    # initialise pygame
    pygame.init()
    screen = pygame.display.set_mode((width,height),1,16)
    
    #load picture
    background= pygame.image.load('parrot.bmp')

    #display picture
    screen.blit(background,(0,0))

    pygame.display.flip()
    
    time.sleep(10)
