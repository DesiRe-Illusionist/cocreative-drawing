from flask import Flask, request, json, render_template
from flask_cors import CORS, cross_origin
import random
import io
import base64
import cv2
import time
import numpy as np
import feature_extraction
import agents
import evaluation
from scipy.signal import argrelextrema
from PIL import Image
# import ml_agent.sketch_rnn_wrapper

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

    updated_components = findUpdatedComponents(cur_components, prev_components)

    responseTurn, transformation, usrAction = decision_tree(stroke, stroke_imag, cur_image, feature_set, updated_components, width, height)

    # Uncomment this to play with custom trained sketch rnn
    # responseTurn = ml_agent.sketch_rnn_wrapper.predict_next_stroke(stroke)

    return json.dumps({"data": responseTurn,"transformation": transformation, "usr_action": usrAction})

def decision_tree(stroke, stroke_image, cur_image, feature_set, updated_components, width, height):

    stroke_candidates = {}
    usrAction = ''

    if feature_set["canvas_diff"]["number_of_components"] == 0:
        print("player added strokes to existing object")
        # player added strokes to existing object
        # strategies:
        #   Apply same stroke to same object
        #   Apply same stroke to different object
        #   SketchRNN completion
        #   If the object is still open, close it.

        usrAction = 'add_to_existing'
        stroke_candidates["enclose_updated"] = agents.enclose_updated_component(updated_components[0]) + (usrAction,)


    elif feature_set["canvas_diff"]["number_of_components"] < 0:
        print("player connected existing objects")
        # player connected existing objects
        # strategies:
        #   using same stroke to connect other objects
        #   using different stroke to connect the same two obejcts
        #   draw a container to enclose the newly connected large componnent

        usrAction = 'connect_existing'
        stroke_candidates["enclose_updated"] = agents.enclose_updated_component(updated_components[0]) + (usrAction,)
        stroke_candidates["strengthen_connection"] = agents.strengthen_connection_agent(stroke) + (usrAction,)

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

                usrAction = 'added_new_closed_object'
                stroke_candidates["scale_in_place"] = agents.scale_in_place_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)
                stroke_candidates["divide_closure"] = agents.divide_closure_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)

            elif feature_set["stroke"]["number_of_contours"] == 1:
                print("new object is one open object")
                # new object is one open object
                # strategies:
                #   translate (shift, scale, etc)
                #   close this object
                #   distort the object

                usrAction = 'added_new_open_object'
                stroke_candidates["close_shape"] = agents.close_shape_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)
                stroke_candidates["distort"] = agents.distort_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)

            else:
                print("new object is a complex object")
                # new object is a complex object
                # strategies:
                #   translate (shift, scale, etc)
                #   draw something around this object
                #   distort the object
                usrAction = 'added_new_complex_object'
                stroke_candidates["shift"] = agents.shift_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)
                stroke_candidates["enclose"] = agents.shift_agent(stroke, stroke_image, cur_image, feature_set, width, height) + (usrAction,)

        else:
            print("player added new object and also added stroke to existing object")
            # player added new object and also added stroke to existing object
            # strategies:
            #   connect the new object with the exist object
            #   repeat the new object (shift, scale, etc)
            usrAction = 'added_new_object_and_existing'
            stroke_candidates["enclose_updated"] = agents.enclose_updated_component(updated_components[0]) + (usrAction,)

    else:
        print("player added multiple objects")
        # strategies:
        #   connect the multiple objects
        #   add same number of objects

        usrAction = 'added_multiple_objects'
        stroke_candidates["enclose_updated"] = agents.enclose_updated_component(updated_components[0]) + (usrAction,)
        stroke_candidates["connect_components"] = agents.connect_components_agent(updated_components) + (usrAction,)

    agent = evaluation.evaluate(cur_image, stroke_candidates, feature_set)
    return stroke_candidates[agent]

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
