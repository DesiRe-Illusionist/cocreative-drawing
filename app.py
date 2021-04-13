from flask import Flask, request, json, render_template
from flask_cors import CORS, cross_origin
#from scipy.stats import bernoulli
import random
import io
import base64
import cv2
import time
import numpy as np
import feature_extraction
from scipy.signal import argrelextrema
from PIL import Image

app = Flask(__name__)
cors = CORS(app)


empty_canvas = cv2.imread("empty_canvas.png")
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/draw', methods=['POST'])
def reactToDraw():
    sessionId = request.get_json().get("session_id")
    turnNum = request.get_json().get("current_turn_number")
    width = request.get_json().get("width")
    height = request.get_json().get("height")
    curBase64Img = request.get_json().get("current_canvas")
    prevBase64Img = request.get_json().get("previous_canvas")
    stroke = request.get_json().get("stroke")

    cur_image = data_uri_to_cv2_img(curBase64Img)
    prev_image = data_uri_to_cv2_img(prevBase64Img)
    stroke_imag = draw_stroke(stroke, width, height)
    #record_canvas_and_stroke(prev_image, cur_image, stroke_imag, sessionId, turnNum)

    feature_set, cur_components, prev_components = extract_features(cur_image, prev_image, stroke_imag, sessionId, turnNum)

    # responseTurn, transformation = shift_agent(stroke, stroke_imag, cur_image, feature_set, width, height)
    # responseTurn, transformation = close_shape_agent(stroke, stroke_imag, cur_image, feature_set, width, height)
    # responseTurn, transformation = distort_agent(stroke, stroke_imag, cur_image, feature_set, width, height)
    # responseTurn, transformation = enclose_agent(stroke, stroke_imag, cur_image, feature_set, width, height)
    # responseTurn, transformation = divide_closure_agent(stroke, stroke_imag, cur_image, feature_set, width, height)
    # responseTurn, transformation = scale_in_place_agent(stroke, stroke_imag, cur_image, feature_set, width, height)

    updated_components = findUpdatedComponents(cur_components, prev_components)
    responseTurn, transformation = decision_tree(stroke, stroke_imag, cur_image, feature_set, updated_components, width, height)


    return json.dumps({"data": responseTurn,"transformation": transformation})

def decision_tree(stroke, stroke_image, cur_image, feature_set, updated_components, width, height):

    random_number = random.random()

    if feature_set["canvas_diff"]["number_of_components"] == 0:
        print("player added strokes to existing object")
        # player added strokes to existing object
        # strategies:
        #   Apply same stroke to same object
        #   Apply same stroke to different object
        #   SketchRNN completion
        #   If the object is still open, close it.


        return enclose_updated_component(updated_components[0])

    elif feature_set["canvas_diff"]["number_of_components"] < 0:
        print("player connected existing objects")
        # player connected existing objects
        # strategies:
        #   using same stroke to connect other objects
        #   using different stroke to connect the same two obejcts
        #   draw a container to enclose the newly connected large componnent

        if random_number > 0.5:
            return enclose_updated_component(updated_components[0])
        else:
            return strengthen_connection_agent(stroke)

    elif feature_set["canvas_diff"]["number_of_components"] == 1:
        if feature_set["stroke"]["number_of_components"] == 1:
            print("player added one object")
            # player added one object
            # certain chance just a new object
            if feature_set["stroke"]["number_of_contours"] == 2 and feature_set["stroke"]["is_closed"]:
                print("new object is an enclosed object")
                # new object is an enclosed object
                # strategies:
                #   Use this new object to fill the enclosure. (shrink)
                #   Use this new object to enclose the object. (expand)
                #   Add line to divide the enclosure (connect)

                if random_number > 0.5:
                    return scale_in_place_agent(stroke, stroke_image, cur_image, feature_set, width, height)
                else:
                    return divide_closure_agent(stroke, stroke_image, cur_image, feature_set, width, height)

            elif feature_set["stroke"]["number_of_contours"] == 1:
                print("new object is one open object")
                # new object is one open object
                # strategies:
                #   translate (shift, scale, etc)
                #   close this object
                #   distort the object

                if random_number > 0.5:
                    return close_shape_agent(stroke, stroke_image, cur_image, feature_set, width, height)
                else:
                    return distort_agent(stroke, stroke_image, cur_image, feature_set, width, height)


            else:
                print("new object is a complex object")
                # new object is a complex object
                # strategies:
                #   translate (shift, scale, etc)
                #   draw something around this object
                #   distort the object


                if random_number > 0.5:
                    return shift_agent(stroke, stroke_image, cur_image, feature_set, width, height)
                else:
                    return enclose_agent(stroke, stroke_image, cur_image, feature_set, width, height)
        else:
            print("player added new object and also added stroke to existing object")
            # player added new object and also added stroke to existing object
            # strategies:
            #   connect the new object with the exist object
            #   repeat the new object (shift, scale, etc)

            return enclose_updated_component(updated_components[0])

    else:
        print("player added multiple objects")
        # strategies:
        #   connect the multiple objects
        #   add same number of objects

        if random_number > 0.5:
            return enclose_updated_component(updated_components[0])
        else:
            return connect_components_agent(updated_components)


def connect_components_agent(updated_components):
    responseStroke = []

    for i in range(len(updated_components)):
        stroke_contours, hierarchy = cv2.findContours(updated_components[i], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        mid_contour = len(stroke_contours[0]) // 2

        x = int(stroke_contours[0][mid_contour][0][0])
        y = int(stroke_contours[0][mid_contour][0][1])
        responseStroke.append([x, y])

    return [responseStroke], "connect components"



def strengthen_connection_agent(strokes):

    responseTurn = []
    for stroke in strokes:
        if (len(stroke) > 2):
            responseStroke = [stroke[0]]
            for i in range(1, len(stroke)-1):
                # x = stroke[i][0] + random.choice([random.randint(-20, -10), random.randint(10, 20)])
                # y = stroke[i][1] + random.choice([random.randint(-20, -10), random.randint(10, 20)])
                x = stroke[i][0] + random.randint(-15, 15)
                y = stroke[i][1] + random.randint(-15, 15)
                responseStroke.append([x,y])
            responseStroke.append(stroke[-1])
            responseTurn.append(responseStroke)

    return responseTurn, "strengthen connection"


def enclose_updated_component(component):

    stroke_contours, hierarchy = cv2.findContours(component, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.convexHull(stroke_contours[0])

    kpCnt = len(stroke_contours[0])

    center_x = 0
    center_y = 0

    for kp in stroke_contours[0]:
        center_x = center_x + kp[0][0]
        center_y = center_y + kp[0][1]

    center_x = center_x / kpCnt
    center_y = center_y / kpCnt

    responseStroke = []
    for i in range(len(hull)):
        x_scale = random.uniform(1.1, 1.4)
        y_scale = random.uniform(1.1, 1.4)
        new_x = (hull[i][0][0] - center_x) * x_scale + center_x
        new_y = (hull[i][0][1] - center_y) * y_scale + center_y
        responseStroke.append([new_x, new_y])
    responseStroke.append(responseStroke[0])

    return [responseStroke], "enclose_updated"

def scale_in_place_agent(stroke, stroke_image, cur_image, feature_set, width, height):

    center_x = feature_set["stroke"]["center_of_mass"]["x"]
    center_y = feature_set["stroke"]["center_of_mass"]["y"]

    scale_rate = random.choice([random.uniform(0.3, 0.7), random.uniform(1.3, 1.7)])

    responseTurn = []
    for s in stroke:
        responseStroke = []
        for point in s:

            responseX = (point[0] - center_x) * scale_rate + center_x
            responseY = (point[1] - center_y) * scale_rate + center_y

            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, "scale_in_place"

def divide_closure_agent(stroke, stroke_image, cur_image, feature_set, width, height):

    # Assume the new stroke is a closed shape.
    stroke_contours, hierarchy = feature_extraction.findContours(stroke_image)
    for i in range(len(stroke_contours)):

        if hierarchy[i][2] > 0:

            inner_contour_idx = hierarchy[i][2] - 1

            mid_contour = len(stroke_contours[inner_contour_idx]) // 2
            start_x = int(stroke_contours[inner_contour_idx][0][0][0])
            start_y = int(stroke_contours[inner_contour_idx][0][0][1])
            end_x = int(stroke_contours[inner_contour_idx][mid_contour][0][0])
            end_y = int(stroke_contours[inner_contour_idx][mid_contour][0][1])

            return [[[start_x, start_y],[end_x, end_y]]], "divide closure"

    return close_shape_agent(stroke, stroke_image, cur_image, feature_set, width, height)


def enclose_agent(stroke, stroke_image, cur_image, feature_set, width, height):

    stroke_contours, hierarchy = feature_extraction.findContours(stroke_image)
    hull = cv2.convexHull(stroke_contours[0])

    center_x = feature_set["stroke"]["center_of_mass"]["x"]
    center_y = feature_set["stroke"]["center_of_mass"]["y"]

    responseStroke = []
    for i in range(len(hull)):
        x_scale = random.uniform(1.1, 1.4)
        y_scale = random.uniform(1.1, 1.4)
        new_x = (hull[i][0][0] - center_x) * x_scale + center_x
        new_y = (hull[i][0][1] - center_y) * y_scale + center_y
        responseStroke.append([new_x, new_y])
    responseStroke.append(responseStroke[0])

    return [responseStroke], "enclose"


def distort_agent(stroke, stroke_image, cur_image, feature_set, width, height):
    stroke_gray = cv2.cvtColor(stroke_image, cv2.COLOR_BGR2GRAY)
    stroke_thresh = cv2.threshold(stroke_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(stroke_thresh,ltype=cv2.CV_32S, connectivity=4)

    x = stats[1, cv2.CC_STAT_LEFT]
    y = stats[1, cv2.CC_STAT_TOP]
    w = stats[1, cv2.CC_STAT_WIDTH]
    h = stats[1, cv2.CC_STAT_HEIGHT]
    cX = int(centroids[1][0])
    cY = int(centroids[1][1])

    cur_image_gray = cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY)
    cur_image_thresh = cv2.threshold(cur_image_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    delta_x = 0
    delta_y = 0
    distortion_rate_x = 1
    distortion_rate_y = 1

    if h / w > 2:
        # tall shape, make shorter
        distortion_rate_y = random.uniform(0.2, 0.5)

        x_pos, y_pos = x, cY
        left_room = 0
        while x_pos >= 0 and cur_image_thresh[x_pos, y_pos] == 0:
            left_room += 1
            x_pos -= 1

        x_pos, y_pos = x + w, cY
        right_room = 0
        while x_pos < width and cur_image_thresh[x_pos, y_pos] == 0:
            right_room += 1
            x_pos += 1

        delta_x = -left_room / 2 if left_room > right_room else right_room / 2
    elif h / w < 0.5:
        # fat shape, make skinnier

        distortion_rate_x = random.uniform(0.2, 0.5)

        x_pos, y_pos = cX, y
        top_room = 0
        while y_pos >= 0 and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            top_room += 1
            y_pos -= 1

        x_pos, y_pos = cX, y + h
        bottom_room = 0
        while y_pos < height and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            bottom_room += 1
            y_pos += 1

        delta_y = -top_room / 2 if top_room > bottom_room else bottom_room / 2
    else:
        # balanced shape, distortion_rate between 0.5 - 1.5
        distortion_rate_x = random.choice([random.uniform(0.3, 0.7), random.uniform(1.3, 1.7)])
        distortion_rate_y = random.choice([random.uniform(0.3, 0.7), random.uniform(1.3, 1.7)])

        x_pos, y_pos = cX, cY
        direction = -1 / feature_set["stroke"]["orientation"]
        i = 1
        right_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX + i
            y_pos = cY + int(direction * i)
            right_room += 1
            i += 1

        x_pos, y_pos = cX, cY
        i = 1
        left_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX - i
            y_pos = cY - int(direction * i)
            left_room += 1
            i += 1

        delta_x = -left_room / 2 if left_room > right_room else right_room / 2
        delta_y = -left_room * direction / 2 if left_room > right_room else right_room * direction / 2

    responseTurn = []
    new_center_x = cX + delta_x
    new_center_y = cY + delta_y
    for s in stroke:
        responseStroke = []
        for point in s:

            responseX = (point[0] - cX) * distortion_rate_x + new_center_x
            responseY = (point[1] - cY) * distortion_rate_y + new_center_y

            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, "distort"


def close_shape_agent(stroke, stroke_image, cur_image, feature_set, width, height):

    responseStroke = [stroke[0][0], stroke[-1][-1]]

    return [responseStroke], "close shape"

def shift_agent(stroke, stroke_image, cur_image, feature_set, width, height):

    stroke_gray = cv2.cvtColor(stroke_image, cv2.COLOR_BGR2GRAY)
    stroke_thresh = cv2.threshold(stroke_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(stroke_thresh,ltype=cv2.CV_32S, connectivity=4)

    x = stats[1, cv2.CC_STAT_LEFT]
    y = stats[1, cv2.CC_STAT_TOP]
    w = stats[1, cv2.CC_STAT_WIDTH]
    h = stats[1, cv2.CC_STAT_HEIGHT]
    cX = int(centroids[1][0])
    cY = int(centroids[1][1])

    cur_image_gray = cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY)
    cur_image_thresh = cv2.threshold(cur_image_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    delta_x = 0
    delta_y = 0
    scale = 1

    if h / w > 2:
        # tall shape, shift left or right
        x_pos, y_pos = x, cY
        left_room = 0
        while x_pos >= 0 and cur_image_thresh[x_pos, y_pos] == 0:
            left_room += 1
            x_pos -= 1

        x_pos, y_pos = x + w, cY
        right_room = 0
        while x_pos < width and cur_image_thresh[x_pos, y_pos] == 0:
            right_room += 1
            x_pos += 1

        probalistic_decision = random.random()
        benchmark = left_room / (left_room + right_room)
        delta_x = -left_room / 2 if probalistic_decision < benchmark else right_room / 2
        scale = clip(left_room/right_room) if probalistic_decision < benchmark else clip(right_room/left_room)
    elif h / w < 0.5:
        # flat shape, shift up or down
        x_pos, y_pos = cX, y
        top_room = 0
        while y_pos >= 0 and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            top_room += 1
            y_pos -= 1

        x_pos, y_pos = cX, y + h
        bottom_room = 0
        while y_pos < height and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            bottom_room += 1
            y_pos += 1

        probalistic_decision = random.random()
        benchmark = top_room / (top_room + bottom_room)
        delta_y = -top_room / 2 if probalistic_decision < benchmark else bottom_room / 2
        scale = clip(top_room/bottom_room) if probalistic_decision < benchmark else clip(bottom_room/top_room)
    else:
        # balanced shape, shift perpendicular to component orientation
        x_pos, y_pos = cX, cY
        direction = -1 / feature_set["stroke"]["orientation"]
        i = 1
        right_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX + i
            y_pos = cY + int(direction * i)
            right_room += 1
            i += 1
        print("right_room: " + str(right_room) + " x_pos: " + str(x_pos) + " y_pos: " + str(y_pos))

        x_pos, y_pos = cX, cY
        i = 1
        left_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX - i
            y_pos = cY - int(direction * i)
            left_room += 1
            i += 1

        print("left_room: " + str(left_room) + " x_pos: " + str(x_pos) + " y_pos: " + str(y_pos))

        probalistic_decision = random.random()
        benchmark = left_room / (left_room + right_room)
        delta_x = -left_room / 2 if probalistic_decision < benchmark else right_room / 2
        delta_y = -left_room * direction / 2 if probalistic_decision < benchmark else right_room * direction / 2
        scale = clip(left_room/right_room) if probalistic_decision < benchmark else clip(right_room/left_room)

    responseTurn = []
    new_center_x = cX + delta_x
    new_center_y = cY + delta_y
    for s in stroke:
        responseStroke = []
        for point in s:

            responseX = (point[0] - cX) * scale + new_center_x
            responseY = (point[1] - cY) * scale + new_center_y

            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, "shift"

def shift_component_agent(stroke, component, cur_image, feature_set, width, height):

    numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(component,ltype=cv2.CV_32S, connectivity=4)

    x = stats[1, cv2.CC_STAT_LEFT]
    y = stats[1, cv2.CC_STAT_TOP]
    w = stats[1, cv2.CC_STAT_WIDTH]
    h = stats[1, cv2.CC_STAT_HEIGHT]
    cX = int(centroids[1][0])
    cY = int(centroids[1][1])

    cur_image_gray = cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY)
    cur_image_thresh = cv2.threshold(cur_image_gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    delta_x = 0
    delta_y = 0
    scale = 1

    if h / w > 2:
        # tall shape, shift left or right
        x_pos, y_pos = x, cY
        left_room = 0
        while x_pos >= 0 and cur_image_thresh[x_pos, y_pos] == 0:
            left_room += 1
            x_pos -= 1

        x_pos, y_pos = x + w, cY
        right_room = 0
        while x_pos < width and cur_image_thresh[x_pos, y_pos] == 0:
            right_room += 1
            x_pos += 1

        probalistic_decision = random.random()
        benchmark = left_room / (left_room + right_room)
        delta_x = -left_room / 2 if probalistic_decision < benchmark else right_room / 2
        scale = clip(left_room/right_room) if probalistic_decision < benchmark else clip(right_room/left_room)
    elif h / w < 0.5:
        # flat shape, shift up or down
        x_pos, y_pos = cX, y
        top_room = 0
        while y_pos >= 0 and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            top_room += 1
            y_pos -= 1

        x_pos, y_pos = cX, y + h
        bottom_room = 0
        while y_pos < height and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            bottom_room += 1
            y_pos += 1

        probalistic_decision = random.random()
        benchmark = top_room / (top_room + bottom_room)
        delta_y = -top_room / 2 if probalistic_decision < benchmark else bottom_room / 2
        scale = clip(top_room/bottom_room) if probalistic_decision < benchmark else clip(bottom_room/top_room)
    else:
        # balanced shape, shift perpendicular to component orientation
        x_pos, y_pos = cX, cY
        direction = -1 / feature_set["stroke"]["orientation"]
        i = 1
        right_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX + i
            y_pos = cY + int(direction * i)
            right_room += 1
            i += 1
        print("right_room: " + str(right_room) + " x_pos: " + str(x_pos) + " y_pos: " + str(y_pos))

        x_pos, y_pos = cX, cY
        i = 1
        left_room = 0
        while isPixelInBoundary(x_pos, y_pos, width, height) and not isPixelInExternalStroke(cur_image_thresh, stroke_thresh, x_pos, y_pos):
            x_pos = cX - i
            y_pos = cY - int(direction * i)
            left_room += 1
            i += 1

        print("left_room: " + str(left_room) + " x_pos: " + str(x_pos) + " y_pos: " + str(y_pos))

        probalistic_decision = random.random()
        benchmark = left_room / (left_room + right_room)
        delta_x = -left_room / 2 if probalistic_decision < benchmark else right_room / 2
        delta_y = -left_room * direction / 2 if probalistic_decision < benchmark else right_room * direction / 2
        scale = clip(left_room/right_room) if probalistic_decision < benchmark else clip(right_room/left_room)

    responseTurn = []
    new_center_x = cX + delta_x
    new_center_y = cY + delta_y
    for s in stroke:
        responseStroke = []
        for point in s:

            responseX = (point[0] - cX) * scale + new_center_x
            responseY = (point[1] - cY) * scale + new_center_y

            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, "shift"

def isPixelInExternalStroke(cur_image_thresh, cur_stroke_thresh, x_pos, y_pos):
    return cur_image_thresh[x_pos, y_pos] != 0 and cur_stroke_thresh[x_pos, y_pos] == 0

def isPixelInBoundary(x_pos, y_pos, width, height):
    return x_pos >= 0 and x_pos < width and y_pos >= 0 and y_pos < height

def clip(x, high = 3, low = 0.3):
    return max(min(x, high), low)

def findUpdatedComponents(cur_components, prev_components):

    updatedComponents = []
    tolerence = 100
    for cur_component in cur_components:
        cur_component_updated = True
        max_overlap = 0
        for prev_component in prev_components:
            if np.count_nonzero(cur_component - prev_component) <= tolerence:
                cur_component_updated = False
                break

        if cur_component_updated:
            updatedComponents.append(cur_component)

    return updatedComponents

def extract_features(cur_image, prev_image, stroke, sessionId, turnNum):

    print("\nSession [" + str(sessionId) + "], Turn [" + str(turnNum) + "]:")
    print("Stroke Features:")
    stroke_num_components, stroke_center_of_mass, stroke_components, _ = feature_extraction.findConnectedComponents(stroke)
    print("Found [" + str(stroke_num_components) + "] components from this stroke")
    print("Center of mass of this stroke is: " + str(stroke_center_of_mass))
    stroke_contours, hierarchy = feature_extraction.findContours(stroke)
    closed = feature_extraction.isClosed(stroke_contours, hierarchy)
    x_origin, y_origin, x_slope, y_slope = feature_extraction.findOrientation(stroke_contours)

    print("\nCurrent Canvas Features:")
    canvas_num_components, canvas_center_of_mass, canvas_components, white_space = feature_extraction.findConnectedComponents(cur_image)
    print("Found [" + str(canvas_num_components) + "] components on Canvas")
    #record_components(canvas_components, sessionId, turnNum)
    print("Center of mass on the canvas is: " + str(canvas_center_of_mass))
    print("Remaining white space percentage on canvas is: " + str(white_space))
    vertical_symmetry_score, horizontal_symmetry_score, up_diagnal_symmetry_score, down_diagnal_symmetry_score = feature_extraction.findSymmetry(cur_image, sessionId, turnNum)

    prev_components = []
    if (turnNum > 1):
        print("Canvas Diff Features:")
        prev_num_components, prev_center_of_mass, prev_components, prev_white_space = feature_extraction.findConnectedComponents(prev_image)
        print("There were [" + str(prev_num_components) + "] components on Canvas before the latest stroke. The delta is " + str(canvas_num_components - prev_num_components))
        print("Center of mass before the latest stroke was: " + str(prev_center_of_mass) + ". The delta is " + str((canvas_center_of_mass[0] - prev_center_of_mass[0], canvas_center_of_mass[1] - prev_center_of_mass[1])))
        print("White space before the latest stroke was: " + str(prev_white_space) + ". The delta is " + str(white_space - prev_white_space))

    feature_set = {
        "session_id" : sessionId,
        "current_turn": turnNum,
        "stroke" : {
            "number_of_components" : stroke_num_components,
            "number_of_contours" : len(stroke_contours),
            "center_of_mass" : {
                "x" : stroke_center_of_mass[0],
                "y" : stroke_center_of_mass[1]
            },
            "is_closed" : closed,
            "orientation" : float(y_slope / x_slope)
        },
        "current_canvas" : {
            "number_of_components" : canvas_num_components,
            "center_of_mass" : {
                "x" : canvas_center_of_mass[0],
                "y" : canvas_center_of_mass[1]
            },
            "whitespace" : white_space,
            "symmetry" : {
                "vertical" : vertical_symmetry_score,
                "horizontal" : horizontal_symmetry_score,
                "diagnal" : down_diagnal_symmetry_score,
                "inverse_diagnal" : up_diagnal_symmetry_score
            }
        },
        "canvas_diff"   : {
            "number_of_components" : canvas_num_components - prev_num_components if turnNum > 1 else canvas_num_components,
            "center_of_mass" : {
                "x" : canvas_center_of_mass[0] - prev_center_of_mass[0] if turnNum > 1 else canvas_center_of_mass[0],
                "y" : canvas_center_of_mass[1] - prev_center_of_mass[1] if turnNum > 1 else canvas_center_of_mass[1]
            },
            "whiltespace" : white_space - prev_white_space if turnNum > 1 else -white_space
        }
    }

    return feature_set, canvas_components, prev_components

def transformation_agent(strokes, width, height):
    #rotate = bernoulli.rvs(p=0.5, size=1)
    rotateOptions = [90, 180, 270]
    scaleOptions = [0.5, 2.0]
    rotateDeg = random.choice(rotateOptions)
    scale = random.choice(scaleOptions)
    # transOptions=['shift','rotate','reflect','scale','shadow','verthatch']
    transOptions=['shift','rotate','reflect','scale']
    transformation=random.choice(transOptions)

    responseTurn = []
    for stroke in strokes:
        responseStroke = []
        midstroke=stroke[round(len(stroke)/2)-1]
        midX = midstroke[0]
        midY = midstroke[1]
        xshift=random.randint(-50,50)
        yshift=random.randint(-50,50)
        for point in stroke:
            xin=point[0]
            yin=point[1]
            if transformation=='reflect':
                responseX = width - xin
                responseY = height - yin
            elif transformation=='rotate':
                responseX = np.cos(rotateDeg) * (xin - midX) - np.sin(rotateDeg) * (yin - midY) + midX
                responseY = np.sin(rotateDeg) * (xin - midX) + np.cos(rotateDeg) * (yin - midY) + midY
            elif transformation=='shift':
                responseX = xin + xshift
                responseY = yin + yshift
            elif transformation=='scale':
                if scale<1:
                    responseX = xin * scale + midX*scale
                    responseY = yin * scale + midY*scale
                elif scale>=1:
                    responseX = xin * scale - midX
                    responseY = yin * scale - midY
            elif transformation == 'shadow' or transformation == 'verthatch':
                    #handle this one in p5
                    responseX = xin
                    responseY = yin
            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, transformation

def data_uri_to_cv2_img(uri):

    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (600, 600))
    valid_image = canvas_diff(img, empty_canvas)

    return valid_image

def canvas_diff(cur_canvas, prev_canvas):
    return 255 + cur_canvas - prev_canvas


def draw_stroke(stroke, width, height):
    image = np.ones((width, height, 3), np.uint8) * 255
    image = cv2.resize(image, (600, 600))
    for i in range(len(stroke)):
        for j in range(len(stroke[i]) - 1):
            cv2.line(image, (int(stroke[i][j][0]), int(stroke[i][j][1])), (int(stroke[i][j+1][0]), int(stroke[i][j+1][1])), (0, 0, 0), 5)
    return image

def record_canvas_and_stroke(prev_canvas, cur_canvas, stroke, sessionId, turnNum):
    canvasId = sessionId + ":turn-" + str(turnNum)
    cv2.imwrite("../Artifacts/canvas/" + canvasId + "prev.png", prev_canvas)
    cv2.imwrite("../Artifacts/canvas/" + canvasId + "cur.png", cur_canvas)

    strokeId = sessionId + ":stroke-" + str(turnNum)
    cv2.imwrite("../Artifacts/strokes/" + strokeId + ".png", stroke)

def record_components(components, sessionId, turnNum):
    fileNamePrefix = str(sessionId) + ":" + str(turnNum) + "-"
    for i in range(len(components)):
        img = Image.fromarray(components[i], 'L')
        img.save("../Artifacts/components/" + fileNamePrefix + "component-" + str(i) + ".png")


#if __name__ == '__main__':
    #api.run(port=8000)
