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
import os

def stitch_images(input_dir, output_dir, filt = 'png'):
    # Grab files
    img_list = os.listdir(input_dir)
    imgs = []

    # Read input images
    for img_name in img_list:
        if filt in img_name:
            img = cv.imread(cv.samples.findFile(input_dir + img_name))
            if img is None:
                print("can't read image " + img_name)
                sys.exit(-1)
            imgs.append(img)

    stitcher = cv.Stitcher.create(cv.Stitcher_SCANS)
    status, pano = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        sys.exit(-1)

    cv.imwrite(output_dir + 'results_scan.png', pano)

    print('Done')

def main():
    input_dir = '/Users/jeremyhyde/Development/plantMonitor/data/raw_images/'
    output_dir = '/Users/jeremyhyde/Development/plantMonitor/data/result_images/'

    stitch_images(input_dir, output_dir)

if __name__ == '__main__':
    main()
