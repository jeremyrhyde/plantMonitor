#!/usr/bin/env python3
"""oled.py
"""
import threading
import time
from queue import Queue, Empty
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from picamera import PiCamera

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

__author__ = "Jeremy Hyde"
__copyright__ = "Copyright 2020"
__credits__ = ["Jeremy Hyde"]

class Camera:

    def __init__(self):

        self.camera = PiCamera()
        self.camera.resolution = (1024, 768)

    def _start_preview(self):
        self.camera.start_preview()

    def _capture(self, file):
        self.camera.capture(file)




def main():
    cam = Camera()

    cam._start_preview()
    time.sleep(2)

    while True:
        user_input = input('Type X to take a picture: ')

        cam._capture('foo.jpg')

        img=mpimg.imread('foo.jpg')
        imgplot = plt.imshow(img)
        plt.show()



if __name__ == "__main__":
    main()
