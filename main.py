from __future__ import print_function
from cv2 import cv2 as cv
import numpy as np
import argparse
import random as rng
import math
#rng.seed(12345)

def thresh_callback(val):
    threshold = val
    # Detect edges using Canny
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)
    
    # Find contours
    _,contours, hierarchy = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    # Find the convex hull object for each contour
    hull_list = []
    for i in range(len(contours)):
        hull = cv.convexHull(contours[i])
        hull_list.append(hull)

    #delete repeated contours
    delete_list=[]
    for i in range(len(contours)):
        for j in range(i+1,len(contours)):
            d= [False for c in contours[j] if c not in contours[i]]
            #not d:j in i
            f= [False for c in contours[i] if c not in contours[j]]
            #not f: i in j
            if not d and not f:# i is j
                if i not in delete_list and j not in delete_list:
                    delete_list.append(j)
    for i in delete_list[::-1]:
        del contours[i]

    # Draw results
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    contour_area=[]
    center_mass=[]
    bounding_box_area=[]
    for i in range(len(contours)):
        if cv.contourArea(contours[i])>=0:
            #random color for each detection
            color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))

            #draw contour
            cv.drawContours(drawing, contours, i, color)

            #draw convexhull
            #cv.drawContours(drawing, hull_list, i, color)

            #draw center of mass
            M = cv.moments(contours[i])
            if M["m00"]!=0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv.circle(drawing, (cX, cY), 3, color, -1)

            #draw fitting line
            # rows,cols = drawing.shape[:2]
            # [vx,vy,x,y] = cv.fitLine(contours[i], cv.DIST_L2,0,0.01,0.01)
            # lefty = int((-x*vy/vx) + y)
            # righty = int(((cols-x)*vy/vx)+y)
            # cv.line(drawing,(cols-1,righty),(0,lefty),color,1)

            #draw bounding rectangle
                rect = cv.minAreaRect(contours[i])
                box = cv.boxPoints(rect)
                box = np.int0(box)
                cv.drawContours(drawing,[box],0,color,2)

                center_mass.append((cX,cY))
                bounding_box_area.append(cv.contourArea(box))
                contour_area.append(cv.contourArea(contours[i]))

            #draw minimun enclosing circle
            # (x,y),radius = cv.minEnclosingCircle(contours[i])
            # center = (int(x),int(y))
            # radius = int(radius)
            # cv.circle(drawing,center,radius,color,2)

            #draw fitting ellipse
            # ellipse = cv.fitEllipse(contours[i])
            # cv.ellipse(drawing,ellipse,(0,255,0),2)

    
    print("contours length",len(contours))

    #calculate weighted center of mass
    area=0
    area_mass_x=0
    area_mass_y=0
    bounding=0
    bounding_mass_x=0
    bounding_mass_y=0
    for i in range(len(center_mass)):
        area+=contour_area[i]
        area_mass_x+=(contour_area[i]*center_mass[i][0])
        area_mass_y+=(contour_area[i]*center_mass[i][1])

        bounding+=bounding_box_area[i]
        bounding_mass_x+=(bounding_box_area[i]*center_mass[i][0])
        bounding_mass_y+=(bounding_box_area[i]*center_mass[i][1])

    print("width",width,"height",height)
    area_mass=(int(area_mass_x/area),int(area_mass_y/area))
    bounding_mass=(int(bounding_mass_x/bounding), int(bounding_mass_y/bounding))
    print("center_mass_contourArea",area_mass)
    cv.circle(drawing, area_mass, 8, (0,255,255), -1)
    print("center_mass_boundingArea",bounding_mass)
    cv.circle(drawing, bounding_mass, 8, (0,0,255), -1)

    # Show in a window
    cv.imshow('Contours', drawing)

# Load source image
src = cv.imread(cv.samples.findFile("blank.png"))
if src is None:
    #print('Could not open or find the image:', args.input)
    print('Could not open or find the image:', "blank.png")
    exit(0)

# Convert image to gray and blur it
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
src_gray = cv.blur(src_gray, (3,3))

# Create Window
source_window = 'Source'
cv.namedWindow(source_window)
cv.imshow(source_window, src)
width=src_gray.shape[0]
height=src_gray.shape[1]

max_thresh = 255
thresh = 100 # initial threshold
cv.createTrackbar('Canny thresh:', source_window, thresh, max_thresh, thresh_callback)
thresh_callback(thresh)

cv.waitKey()
