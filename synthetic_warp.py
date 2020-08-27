# new data creation
import cv2
import os
import numpy as np
import math
import random

def rotateImage(inp, alpha, beta, gamma, dx, dy, dz, f):
    # convert to radians
    alpha = (alpha)*math.pi/180.
    beta = (beta)*math.pi/180.
    gamma = (gamma)*math.pi/180.
    # get width and height for ease of use in matrices
    w, h, channels = inp.shape
    # Projection 2D -> 3D matrix
    A1 = np.matrix(
              [[1, 0, -w/2],
              [0, 1, -h/2],
              [0, 0,    0],
              [0, 0,    1]])
    # Rotation matrices around the X, Y, and Z axis
    RX = np.matrix([[
              1,          0,           0, 0],
              [0, math.cos(alpha), -math.sin(alpha), 0],
              [0, math.sin(alpha),  math.cos(alpha), 0],
              [0,          0,           0, 1]])
    RY = np.matrix([[
              math.cos(beta), 0, -math.sin(beta), 0],
              [0, 1,          0, 0],
              [math.sin(beta), 0,  math.cos(beta), 0],
              [0, 0,          0, 1]])
    RZ = np.matrix([[
              math.cos(gamma), -math.sin(gamma), 0, 0],
              [math.sin(gamma),  math.cos(gamma), 0, 0],
              [0,          0,           1, 0],
              [0,          0,           0, 1]])
    # Composed rotation matrix with (RX, RY, RZ)
    R = np.matmul(RX, np.matmul(RY, RZ))
    # Translation matrix
    T = np.matrix([[
             1, 0, 0, dx],
             [0, 1, 0, dy],
             [0, 0, 1, dz],
             [0, 0, 0, 1]])
    # 3D -> 2D matrix
    A2 = np.matrix([[
              f, 0, w/2, 0],
              [0, f, h/2, 0],
              [0, 0,   1, 0]])
    
    # Final transformation matrix
    trans = np.matmul(A2,np.matmul(T, np.matmul(R, A1)))
    
    # Apply matrix transformation
    return cv2.warpPerspective(inp, trans, (w,h))

    
def generate(path,warp_in,warp_out,trim_in,trim_out,rotate_max,trim):
    num_images = 1000 # replace with 100000 for all data
    trim = 50
    percent = -1
    
    for i in range(num_images): 
        cur_percent = (i+1)/num_images*100-1
        if cur_percent > percent:
            percent = int(cur_percent)+1
            print(str(percent)+"%")
        
        imgName = str(i).zfill(6)+".png"

        theta = []
        for j in range(3):
            theta.append(random.random()*rotate_max*2-rotate_max) # -rotate_max to rotate_max degrees

        # warp and trim the warp images
        for j in range(len(warp_in)):
            inPath = path+warp_in[j]+imgName
            outPath = path+warp_out[j]+imgName

            im_original = cv2.imread( inPath)
            h, w, channels = im_original.shape

            # rotateImage(inp, alpha, beta, gamma, dx, dy, dz, f)
            im_new = rotateImage(im_original, theta[0], theta[1], theta[2], 0, 0, w/2, w/2);

            trimmed = im_new[trim:h-trim, trim:w-trim]
            
            cv2.imwrite(outPath,trimmed)

        # trim the trim only images
        for j in range(len(trim_in)):
            inPath = path + trim_in[j] + imgName
            outPath = path + trim_out[j] + imgName

            im_original = cv2.imread( inPath)
            h, w, channels = im_original.shape
            trimmed = im_original[trim:h-trim, trim:w-trim]

            cv2.imwrite(outPath,trimmed)


def initialize():
    path = "G:/synthetic/deep_mag_data/train/" # training folder location
    in_dirs = ["frameB/","frameC/","amplified/"] # directories with images to warp and trim (relative to path)
    out_dirs = ["BNew/","CNew/","amplifiedNew/"] # corresponding directories to put warped output (relative to path)
    trim_in = ["frameA/"] # directories with images to just trim (relative to path)
    trim_out = ["ANew/"] # corresponding directories to put trimmed output (relative to path)
    rotate_max = 10 # max rotate for each axis in degrees
    trim_amount = 50 # number of pixels to trim around border of image

    for directory in in_dirs+trim_in:
        assert os.path.isdir(path+directory)

    for directory in out_dirs+trim_out:
        if not os.path.exists(path+directory):
            os.makedirs(path+directory)


    generate(path,in_dirs,out_dirs,trim_in,trim_out,rotate_max,trim_amount)

initialize()

    
    
