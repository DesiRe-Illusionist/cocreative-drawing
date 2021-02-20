from flask import Flask, request, json
from flask_cors import CORS, cross_origin

api = Flask(__name__)
cors = CORS(api)

@api.route('/draw', methods=['POST'])
def reactToDraw():
  strokes = request.get_json().get("data")
  width = request.get_json().get("width")
  height = request.get_json().get("height")
  responseTurn = []
  for stroke in strokes:
    responseStroke = []
    for point in stroke:
      responseX = width - point[0]
      responseY = height - point[1]
      responseStroke.append([responseX, responseY])
    responseTurn.append(responseStroke)

  return json.dumps({"data": responseTurn})

if __name__ == '__main__':
    api.run(port=8000)