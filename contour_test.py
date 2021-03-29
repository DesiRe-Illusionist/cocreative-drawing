from __future__ import print_function
from cv2 import cv2 as cv
import numpy as np
import argparse
import random as rng
import math
def thresh_callback(val,src_img):
    
    src = cv.imread(cv.samples.findFile(src_img))
    if src is None:
        #print('Could not open or find the image:', args.input)
        print('Could not open or find the image:', src_img)
        exit(0)

    # Convert image to gray and blur it
    src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    src_gray = cv.blur(src_gray, (3,3))

    #width=src_gray.shape[0]
    #height=src_gray.shape[1]

    # Detect edges using Canny
    threshold = val
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)

    # Find contours
    _,contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #print(len(contours),hierarchy)

    #delete all repeated contours
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

    
    #drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    contour_area=[]
    center_mass=[]
    bounding_box_area=[]
    for i in range(len(contours)):
        if cv.contourArea(contours[i])>=0:
            #center of mass
            M = cv.moments(contours[i])
            if M["m00"]!=0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

            #bounding rectangle
                rect = cv.minAreaRect(contours[i])
                box = cv.boxPoints(rect)
                box = np.int0(box)

                center_mass.append((cX,cY))
                bounding_box_area.append(cv.contourArea(box))
                contour_area.append(cv.contourArea(contours[i]))

    
    #print("contours length",len(contours))
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

    #print("width",width,"height",height)
    area_mass=(int(area_mass_x/area),int(area_mass_y/area))
    bounding_mass=(int(bounding_mass_x/bounding), int(bounding_mass_y/bounding))
    print("center_mass_contour",area_mass)
    print("dist to center",math.dist(area_mass,(600,600)))
    #cv.circle(drawing, area_mass, 8, (0,255,255), -1)
    print("center_mass_bounding",bounding_mass)
    print("dist to center",math.dist(bounding_mass,(600,600)))
    #cv.circle(drawing, bounding_mass, 8, (0,0,255), -1)
    #print(max_c)
    min_dist=min(math.dist(area_mass,(600,600)),math.dist(bounding_mass,(600,600)))
    return min_dist

# max_thresh = 255
# thresh = 100 # initial threshold
# thresh_callback(thresh)

cv.waitKey()
