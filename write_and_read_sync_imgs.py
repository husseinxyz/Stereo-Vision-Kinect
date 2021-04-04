#!/usr/bin/env python
# script with live visualization of depth map and RGB frame
# and possibility to record the pair of images when a key is pressed
# + includes too a conveninent function to read RGB + D data recorded with this script

import numpy as np
import freenect
import cv2


def get_depth_and_video():
    # return original 16 bits depth values (in fact 11 bits) + pretty 8 bits depth image easy to visualize + rgb image
    depth_map = freenect.sync_get_depth()[0]
    rgb = freenect.sync_get_video()[0]
    # depth is coded in 16 bits but should have values in [[0 ; 2047]] (11 bits)
    np.clip(depth_map, 0, 2**10 - 1, depth_map)
    depth_pretty = np.array(depth_map)
    depth_pretty >>= 2
    depth_pretty = depth_pretty.astype(np.uint8)
    return depth_map, depth_pretty, rgb[:,:,::-1] # RGB -> BGR


def write_shot(depth, depth_pretty, bgr, n, todir='./shots'):
    # write a shot to number n
    cv2.imwrite('{}/{:02d}_depth.png'.format(todir, n),depth, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
    cv2.imwrite('{}/{:02d}_depth_pretty.png'.format(todir, n),depth_pretty, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
    cv2.imwrite('{}/{:02d}_rgb.png'.format(todir, n),bgr, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])

def open_shot(n, fromdir='./shots'):
    # open a shot according to its number
    depth = cv2.imread('{}/{:02d}_depth.png'.format(fromdir, n), cv2.IMREAD_ANYDEPTH)
    depth_pretty = cv2.imread('{}/{:02d}_depth_pretty.png'.format(fromdir, n))
    bgr = cv2.imread('{}/{:02d}_rgb.png'.format(fromdir, n))
    return depth, depth_pretty, bgr


def main(counter):
    while 1:
        depth, depth_pretty, bgr = get_depth_and_video()
        cv2.imshow('Depth', depth_pretty)
        cv2.imshow('Video', bgr)
        pressedkey = cv2.waitKey(10)
        if pressedkey == 27:
            cv2.destroyAllWindows()
            break
        elif pressedkey != -1:
            # save RGB + D images
            print("Save data {}!".format(counter))
            write_shot(depth, depth_pretty, bgr, counter)
            counter += 1

if __name__ == "__main__":
    cv2.namedWindow('Depth')
    cv2.namedWindow('Video')
    print('Press ESC in window to stop')

    counter = 0 # init counter to number the images
    main(counter)
