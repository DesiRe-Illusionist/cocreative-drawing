from flask import Flask, request, json
from flask_cors import CORS, cross_origin
#from scipy.stats import bernoulli
import random
import io
import base64
import cv2
import time
import numpy as np
import feature_extraction
from PIL import Image

api = Flask(__name__)
cors = CORS(api)

empty_canvas = cv2.imread("empty_canvas.png")

@api.route('/draw', methods=['POST'])
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
    record_canvas_and_stroke(prev_image, cur_image, stroke_imag, sessionId, turnNum)

    feature_set = extract_features(cur_image, prev_image, stroke_imag, sessionId, turnNum)

    responseTurn, transformation = shift_agent(stroke, stroke_imag, cur_image, feature_set, width, height)

    return json.dumps({"data": responseTurn,"transformation": transformation})

def decision_tree(feature_set):
    if feature_set["canvas_diff"]["number_of_component"] == 0:
        # player added strokes to existing object
        # strategies:
        #   Apply same stroke to same object
        #   Apply same stroke to different object
        #   SketchRNN completion
        #   If the object is still open, close it.
    elif feature_set["canvas_diff"]["number_of_component"] < 0:
        # player connected existing objects
        # strategies:
        #   using same stroke to connect other objects
        #   using different stroke to connect the same two obejcts
        #   draw a container to enclose the newly connected large componnent
    elif feature_set["canvas_diff"]["number_of_component"] == 1:
        if feature_set["stroke"]["number_of_component"] == 1:
            # player added one object
            # certain chance just a new object
            if feature_set["stroke"]["number_of_contours"] == 2 and feature_set["stroke"]["is_closed"]:
                # new object is an enclosed object
                # strategies: 
                #   fill the enclosure. (shrink)
                #   Enclose the object. (expand)
                #   Add line to divide the enclosure (connect)
            elif feature_set["stroke"]["number_of_contours"] == 1
                # new object is one open object
                # strategies:
                #   translate (shift, scale, etc)
                #   close this object
                #   distort the object
            else:
                # new object is a complex object
                # strategies:
                #   translate (shift, scale, etc)
                #   draw something around this object
                #   distort the object
        else:
            # player added new object and also added stroke to existing object
            # strategies:
            #   connect the new object with the exist object
            #   repeat the new object

    else:
        # player added multiple objects
        # strategies:
        #   connect the multiple objects
        #   add same number of objects

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
    record_components(canvas_components, sessionId, turnNum)
    print("Center of mass on the canvas is: " + str(canvas_center_of_mass))
    print("Remaining white space percentage on canvas is: " + str(white_space))
    vertical_symmetry_score, horizontal_symmetry_score, up_diagnal_symmetry_score, down_diagnal_symmetry_score = feature_extraction.findSymmetry(cur_image, sessionId, turnNum)

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
            "number_of_contours" : len(stroke_contours)
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
            "number_of_component" : canvas_num_components - prev_num_components if turnNum > 1 else canvas_num_components,
            "center_of_mass" : {
                "x" : canvas_center_of_mass[0] - prev_center_of_mass[0] if turnNum > 1 else canvas_center_of_mass[0],
                "y" : canvas_center_of_mass[1] - prev_center_of_mass[1] if turnNum > 1 else canvas_center_of_mass[1]
            },
            "whiltespace" : white_space - prev_white_space if turnNum > 1 else -white_space
        }
    }

    return feature_set

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
    valid_image = canvas_diff(img, empty_canvas)

    return valid_image

def canvas_diff(cur_canvas, prev_canvas):
    return 255 + cur_canvas - prev_canvas

def draw_stroke(stroke, width, height):
    image = np.ones((width, height, 3), np.uint8) * 255
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


if __name__ == '__main__':
    api.run(port=8000)
