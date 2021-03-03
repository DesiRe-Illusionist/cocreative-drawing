from flask import Flask, request, json
from flask_cors import CORS, cross_origin
#from scipy.stats import bernoulli
import random
import numpy as np

api = Flask(__name__)
cors = CORS(api)

@api.route('/draw', methods=['POST'])
def reactToDraw():
  strokes = request.get_json().get("data")
  width = request.get_json().get("width")
  height = request.get_json().get("height")

  #rotate = bernoulli.rvs(p=0.5, size=1)
  rotateOptions = [90, 180, 270]
  rotateDeg = random.choice(rotateOptions)
  transOptions=['shift','rotate','reflect']
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
        responseStroke.append([responseX, responseY])
    responseTurn.append(responseStroke)

  return json.dumps({"data": responseTurn,"transformation": transformation})

if __name__ == '__main__':
    api.run(port=8000)
