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

api = Flask(__name__)
cors = CORS(api)

@api.route('/draw', methods=['POST'])
def reactToDraw():
    base64Img = request.get_json().get("canvas")
    strokes = request.get_json().get("data")
    width = request.get_json().get("width")
    height = request.get_json().get("height")

    responseTurn, transformation = transformation_agent(strokes, width, height)

    image = data_uri_to_cv2_img(base64Img)
    vert_sym, hori_sym, diag_sym, op_diag_sym = feature_extraction.findSymmetry(image)
    vert_bal, hori_bal, diag_bal, op_diag_bal = feature_extraction.findBalance(image)

    return json.dumps({"data": responseTurn,"transformation": transformation})

def transformation_agent(strokes, width, height):
    #rotate = bernoulli.rvs(p=0.5, size=1)
    rotateOptions = [90, 180, 270]
    scaleOptions = [0.5, 2.0]
    rotateDeg = random.choice(rotateOptions)
    scale = random.choice(scaleOptions)
    transOptions=['shift','rotate','reflect','scale','shadow','verthatch']
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
                    responseX = xin * scale + midX*scale;
                    responseY = yin * scale + midY*scale;
                elif scale>=1:
                    responseX = xin * scale - midX;
                    responseY = yin * scale - midY;
            elif transformation == 'shadow' or transformation == 'verthatch':
                    #handle this one in p5
                    responseX = xin;
                    responseY = yin;
            responseStroke.append([responseX, responseY])
        responseTurn.append(responseStroke)

    return responseTurn, transformation

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/Canvas/" + str(time.time()) + ".png", img)
    return img

if __name__ == '__main__':
    api.run(port=8000)
