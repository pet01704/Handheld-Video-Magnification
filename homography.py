# apply homography to video
import cv2
import numpy as np
import os

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15
matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)

def alignImages(im1,im2):
  # Convert images to grayscale
  im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
  im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
  
  # Detect ORB features and compute descriptors.
  orb = cv2.ORB_create(MAX_FEATURES)
  keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
  keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)
  
  # Match features.
  
  #if descriptors1 is None or descriptors2 is None:
  #    return im1
  
  matches = matcher.match(descriptors1, descriptors2, None)

  # Sort matches by score
  matches.sort(key=lambda x: x.distance, reverse=False)

  # Remove not so good matches
  numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
  matches = matches[:numGoodMatches]
  
  # Extract location of good matches
  points1 = np.zeros((len(matches), 2), dtype=np.float32)
  points2 = np.zeros((len(matches), 2), dtype=np.float32)

  for i, match in enumerate(matches):
    points1[i, :] = keypoints1[match.queryIdx].pt
    points2[i, :] = keypoints2[match.trainIdx].pt
  # Find homography
  h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

  # Use homography
  height, width, channels = im2.shape
  im1Reg = cv2.warpPerspective(im1, h, (width, height))
  
  return im1Reg

def alignFrames(input_frames,output_frames):
  lastframe = None
  framenum = 0
  for image_path in os.listdir(input_frames):
    nextframe = cv2.imread(input_frames+"/"+image_path)
    if lastframe is not None:
      nextframe = alignImages(nextframe,lastframe)
    cv2.imwrite(output_frames+"/"+str(framenum)+".png",nextframe)
    lastframe = nextframe
    framenum+=1

"""
def alignVideo(video,intermediate_file,display_results):
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    aligned = cv2.VideoWriter(intermediate_file,cv2.VideoWriter_fourcc('m','p','4','v'), 20, (frame_width,frame_height))
    lastframe = None
    framenum = 0
    while(video.isOpened()):
        ret, frame = video.read()
        
        if ret==True:
            
            # change frame
            if framenum != 0:
                # todo: fix this hack
                try:
                    frame = alignImages(frame,lastframe)
                except:
                    pass
            #if framenum > 2:
            #  break
            aligned.write(frame)

            lastframe = frame
            framenum+=1
        else:
            break

    video.release()
    aligned.release()
"""


    
      
