# source: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
 
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
 
# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])
 
# initialize the first frame in the video stream
firstFrame = None