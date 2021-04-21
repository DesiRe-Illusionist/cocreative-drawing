import sys
import cv2
import numpy
import time
import math
import random
from PIL import Image


from phasepack.phasesym import phasesym
from phasepack.phasecongmono import phasecongmono

def main():
    imagePath = sys.argv[1]
    img = cv2.imread(imagePath)

    contours, hierarchy = findContours(img)
    closed = isClosed(contours, hierarchy)

def findSymmetry(img, sessionId, turnNum):

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img_gray,200,255,0)
    phaseSym, orientation, totalEnergy, T = phasesym(thresh, norient=4, polarity=0)

    nonContourSym = (phaseSym - 1 + thresh/255).clip(0)

    vertical_phaseSym = numpy.absolute(numpy.multiply(nonContourSym, numpy.cos(orientation / 180 * numpy.pi)))
    horizontal_phaseSym = numpy.multiply(nonContourSym, numpy.sin(orientation / 180 * numpy.pi))
    upward_diagnal_phaseSym = numpy.absolute(numpy.multiply(nonContourSym, numpy.sin((orientation - 45)/ 180 * numpy.pi)))
    downward_diagnal_phaseSym = numpy.absolute(numpy.multiply(nonContourSym, numpy.sin((orientation + 45)/ 180 * numpy.pi)))

    fileNamePrefix = str(sessionId) + ":" + str(turnNum) + "-"
    img = Image.fromarray((vertical_phaseSym * 255).astype(numpy.uint8), 'L')
    #img.save("../Artifacts/phaseSym/" + fileNamePrefix + "vert.png")

    img = Image.fromarray((horizontal_phaseSym * 255).astype(numpy.uint8), 'L')
    #img.save("../Artifacts/phaseSym/" + fileNamePrefix + "hori.png")

    img = Image.fromarray((upward_diagnal_phaseSym * 255).astype(numpy.uint8), 'L')
    #img.save("../Artifacts/phaseSym/" + fileNamePrefix + "up_diag.png")

    img = Image.fromarray((downward_diagnal_phaseSym * 255).astype(numpy.uint8), 'L')
    #img.save("../Artifacts/phaseSym/" + fileNamePrefix + "down_diag.png")

    normalization_constant = 150000
    vertical_symmetry_score = numpy.sum(vertical_phaseSym) / normalization_constant
    print("vertical symmetry score for image is " + str(vertical_symmetry_score))
    horizontal_symmetry_score = numpy.sum(horizontal_phaseSym) / normalization_constant
    print("horizontal symmetry score for image is " + str(horizontal_symmetry_score))
    down_diagnal_symmetry_score = numpy.sum(downward_diagnal_phaseSym) / normalization_constant
    print("diagnal symmetry score for image is " + str(down_diagnal_symmetry_score))
    up_diagnal_symmetry_score = numpy.sum(upward_diagnal_phaseSym) / normalization_constant
    print("opposite diagnal symmetry score for image is " + str(up_diagnal_symmetry_score))
    print("\n")
    return vertical_symmetry_score, horizontal_symmetry_score, up_diagnal_symmetry_score, down_diagnal_symmetry_score

def findConnectedComponents(src):

    img_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh,ltype=cv2.CV_32S, connectivity=4)

    total_boxed_area = 0
    total_area=0
    area_mass_x=0
    area_mass_y=0
    components = []
    # fileNamePrefix = sessionId + ":" + turnNum + "-"
    for i in range(1, numLabels):
        # extract the connected component statistics and centroid for
        # the current label
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        (cX, cY) = centroids[i]

        total_boxed_area += w * h
        total_area += area
        area_mass_x += cX * area
        area_mass_y += cY * area

        # output = src.copy()
        # cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
        # cv2.circle(output, (int(cX), int(cY)), 4, (0, 0, 255), -1)

        # construct a mask for the current connected component by
        # finding a pixels in the labels array that have the current
        # connected component ID
        componentMask = (labels == i).astype("uint8") * 255
        components.append(componentMask)
        # img = Image.fromarray(componentMask, 'L')
        # img.save("../Artifacts/components/" + fileNamePrefix + "component-" + str(i) + ".png")
        # show our output image and connected component mask
        # cv2.imshow("Output", output)
        # cv2.imshow("Connected Component", componentMask)
        # cv2.waitKey(0)

    center_of_mass = (int(area_mass_x/total_area),int(area_mass_y/total_area))
    white_space = 1 - total_boxed_area / (src.shape[0] * src.shape[1])
    return numLabels-1, center_of_mass, components, white_space

def isClosed(stroke_contours, hierarchy):

    # empty = numpy.zeros((600, 600, 3), numpy.uint8)
    for i in range(len(stroke_contours)):

        # cv2.drawContours(empty, [stroke_contours[i]], -1, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 3)
        # cv2.imshow("contour", empty)
        # cv2.waitKey(0)

        if hierarchy[i][2] > 0:
            print("This stroke DOES contains closed contour.")
            return True
    print("This stroke does NOT contains closed contour.")
    return False

def findOrientation(stroke_contours):

    # w = 500
    x_pos = 0
    y_pos = 0
    x_vec = 0
    y_vec = 0
    total_area = 0
    for contour in stroke_contours:
        vx, vy, cx, cy = cv2.fitLine(contour, distType=cv2.DIST_L1, param=0, reps=0.01, aeps=0.01)
        area = cv2.contourArea(contour)

        # cv2.line(stroke, (int(cx), int(cy)), (int(cx+vx*w), int(cy+vy*w)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 1, 255)
        # cv2.imshow("line", stroke)

        total_area += area
        x_pos += cx * area
        y_pos += cy * area
        x_vec += vx * area
        y_vec += vy * area

    x_origin = x_pos / total_area
    y_origin = y_pos / total_area
    x_slope = x_vec / total_area
    y_slope = y_vec / total_area

    # cv2.line(stroke, (int(x_origin),int(y_origin)), (int(x_origin + x_slope * w), int(y_origin + y_slope * w)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), thickness=3, lineType=8)
    # cv2.imshow("weighted_line", stroke)
    # cv2.waitKey(0)
    print("This stroke has an orientation along the slope of " + str(y_slope/x_slope))
    return x_origin, y_origin, x_slope, y_slope

def findContours(stroke, threshold=200):

    img_gray = cv2.cvtColor(stroke, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img_gray,200,255,0)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = contours[1:]
    hierarchy = hierarchy[0][1:]

    print("Number of contours found in this stroke is " + str(len(contours)))

    return contours, hierarchy



if __name__ == '__main__':
    main()
