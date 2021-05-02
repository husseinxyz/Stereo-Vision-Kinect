# Stereo Vision

## Introduction
Scripts to read RGB data, show live visualization of depth map and RGB frames, depth in distances from Kinect, computes points 3D coordinates from depth, and more!

## Overview of the Repository
In this repo, you'll find :
* `shots`: plots of depth, and visualizations on frames.
* `rgbd.py`: get distances in meter from depth given by Kinect, computes points 3D coordinates from depth, and more!.
* `write_and_read_sync_imgs.py`: script with live visualization of depth map and RGB frame, read code for more details.

## Getting Started
1.  Clone repo: `git clone https://github.com/husseinxyz/Stereo-Vision-Kinect.git`
2.  Install dependencies:
    ```
    conda create -n stereo-vision python=3.7
    conda activate stereo-vision
    pip install -r requirements.txt
    ```
3. Run `rgbd.py`, and ` write_and_read_sync_imgs.py` depending on your application ;)
