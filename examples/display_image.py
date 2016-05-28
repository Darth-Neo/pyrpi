#!/usr/bin/python
import os
import pygame, sys
from pygame.locals import *

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
