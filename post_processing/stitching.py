#!/usr/bin/env python

'''
Stitching sample
================

Show how to use Stitcher API from python in a simple way to stitch panoramas
or scans.
'''

import numpy as np
import cv2 as cv

import sys
import os, glob

def stitch_images(input_dir, output_file, filt = '*.png'):
    # Grab files
    os.chdir(input_dir)
    imgs = []

    # Read input images
    for file in glob.glob(filt):
        print(file)
        img = cv.imread(cv.samples.findFile(input_dir + file))
        if img is None:
            print("can't read image ")
            sys.exit(-1)
        imgs.append(img)

    print('Stitching image')
    stitcher = cv.Stitcher(cv.Stitcher_SCANS)
    status, pano = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        sys.exit(-1)

    cv.imwrite(output_file, pano)

    print('Done')

def main():
    input_dir = '/home/pi/plantmonitor/data/raw_images/'
    output_dir = '/home/pi/plantmonitor/data/result_images/results.png'
    filter = 'route_line_*.png'

    stitch_images(input_dir, output_dir, filter)

if __name__ == '__main__':
    main()
