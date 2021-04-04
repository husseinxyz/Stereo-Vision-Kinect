#!/usr/bin/env python
import numpy as np
import cv2
import pptk # pip install pptk # !! Ubuntu users, pptk has a bug with libz.so.1, see how to do a new symlink in https://github.com/heremaps/pptk/issues/3
#from write_and_read_sync_imgs import open_shot
#Note: Be careful, "depths" given by Kinect are not actually "depths" dut disparities. In common language, these terms are often considered the same.

#%%
def open_shot(n, fromdir='./shots'):
    # open a shot according to its number
    depth = cv2.imread('{}/{:02d}_depth.png'.format(fromdir, n), cv2.IMREAD_ANYDEPTH)
    depth_pretty = cv2.imread('{}/{:02d}_depth_pretty.png'.format(fromdir, n))
    bgr = cv2.imread('{}/{:02d}_rgb.png'.format(fromdir, n))
    return depth, depth_pretty, bgr

#%%
def raw_depth_to_meters(raw_disp):
    # get distances in meter from depth given by Kinect
    # Kinect computes the depth, but outputs a value coded a specific way in [[0;2047]] on 11 bits
    # informations on https://openkinect.org/wiki/Imaging_Information
    m_depth = np.zeros_like(raw_disp, dtype=np.float)
    # raw_disp must be transformed, some explanations in https://wiki.ros.org/kinect_calibration/technical
    f = 580. # focal IR cam
    m_b = 0.075 # baseline for depth sensor
    m_depth[raw_disp < 2047] = 8.*f*m_b / (1090 - raw_disp[raw_disp < 2047])
    return m_depth

#%%
def xyz_from_depth_meters(m_depth):
    # computes points 3D coordinates from depth
    xyz = np.zeros((m_depth.shape[0],m_depth.shape[1],3), dtype=np.float)
    f = 580. # focal IR cam
    cx = 320. # optical center x
    cy = 240. # optical center y
    indi = np.indices(m_depth.shape)
    xyz[:,:,0] = (indi[1] - cx) * m_depth / f # we know x and y at distance f, so we can compute at distance z by *z/f :) no need of complicated matrix
    xyz[:,:,1] = (indi[0] - cy) * m_depth / f
    xyz[:,:,2] = m_depth
    # flatten to a list of points
    xyz = xyz.reshape((-1,3))
    # filter points where all XYZ coordinates are 0
    xyz = xyz[np.any(xyz != 0, axis=1)]
    # filter points where Z is too large, 5 meters seems ok
    xyz = xyz[xyz[:,2] <= 5.]
    return xyz

#%%
def color_of_xyz(xyz, bgr_img):
    # associate colors to depth / 3D points
    xyz_h = np.concatenate((xyz.T, np.ones((1,xyz.shape[0]))), axis=0) # homogeneous version
    # back-project each 3D point in RGB camera and get closest color (no interpolation to get faster)
    R = np.identity(3, dtype=np.float) # rotation matrix from IR to RGB camera
    T = np.array([[-0.025], [0.], [0.]]) # meters, translation from IR to RGB camera
    transfo = np.vstack( (np.hstack((R,T)), np.array([0., 0., 0., 1.])) )
    xyz_rgb_h = np.matmul(transfo, xyz_h)
    cx = 320. # optical center x
    cy = 240. # optical center y
    f = 525 # focal RGB camera ; considering horiz and vertical the same ie no skew and squared pixels
    Ic = np.array([[f, 0, cx, 0], \
                   [0, f, cy, 0], \
                   [0, 0, 1., 0]]) # calibration matrix of RGB camera, no matter the unit/scale of input XYZ points of real world
    # projection of 3D points in RGB image in homogeneous coordinates
    uv_rgb_h = np.matmul(Ic, xyz_rgb_h)
    # de-homogeneate coordinates in image and round them
    uv_rgb = np.vstack((uv_rgb_h[1,:] / uv_rgb_h[2,:], uv_rgb_h[0,:] / uv_rgb_h[2,:])).astype(np.int16) # + in the same time, put first coords in row then cols for numpy, ie y,x instead of x,y
    # check if all points will belong to image size
    uv_rgb = np.maximum(uv_rgb, 0)
    uv_rgb[0,:] = np.minimum(uv_rgb[0,:], 479) # 480 among Y
    uv_rgb[1,:] = np.minimum(uv_rgb[1,:], 639) # 640 among X
    rgb_colors = bgr_img[uv_rgb[0,:],uv_rgb[1,:],::-1] # ::-1 instead of : to pass from BGR (opencv) to RGB
    return rgb_colors


#%%
def main(shot):
    depth, depth_pretty, bgr = open_shot(shot) # open RGB and D data of the shot
    cv2.imshow('Depth', depth_pretty) # display depth
    cv2.imshow('RGB', bgr) # display RGB

    # depth map in meters
    m_depth = raw_depth_to_meters(depth)

    # show in 3D point cloud
    xyz = xyz_from_depth_meters(m_depth)
    # no-colored version
    v = pptk.viewer(xyz) # show 3D point cloud
    v.set(point_size=0.001)

    #add color information
    rgb_colors = color_of_xyz(xyz, bgr)
    v.attributes(rgb_colors / 255.)


    while 1:
        if cv2.waitKey(10) == 27:
            cv2.destroyAllWindows()
            v.close()
            break

#%%
if __name__ == "__main__":
    cv2.namedWindow('Depth')
    cv2.namedWindow('RGB')
    print('Press ESC in window to stop')

    shot = 10 # shot number to open
    main(shot)
