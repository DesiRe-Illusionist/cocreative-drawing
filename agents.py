import random
import cv2
import numpy as np
import feature_extraction

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

def isPixelInExternalStroke(cur_image_thresh, cur_stroke_thresh, x_pos, y_pos):
    return cur_image_thresh[x_pos, y_pos] != 0 and cur_stroke_thresh[x_pos, y_pos] == 0

def isPixelInBoundary(x_pos, y_pos, width, height):
    return x_pos >= 0 and x_pos < width and y_pos >= 0 and y_pos < height

def clip(x, high = 3, low = 0.3):
    return max(min(x, high), low)