from flask import Flask, request, json
from flask_cors import CORS, cross_origin

# from scipy.stats import bernoulli
import random
import numpy as np
import ml_agent.sketch_rnn_wrapper as skrnn
import random

TEST_LINE = np.array(
    [
        [-2.980674, 2.4316025, 0.0],
        [1.9609697, -0.7843879, 0.0],
        [1.0197042, -0.7843879, 0.0],
        [0.86282665, -0.7843879, 0.0],
        [0.6275103, -0.86282665, 0.0],
    ]
)

api = Flask(__name__)
cors = CORS(api)


@api.route("/draw", methods=["POST"])
def reactToDraw():
    strokes = request.get_json().get("data")
    width = request.get_json().get("width")
    height = request.get_json().get("height")

    print("---------------Recieved Stroke---------------")
    boolean = bool(random.getrandbits(1))
    print(f"---------------Blind : {str(boolean)}---------------")
    responseTurn = skrnn.predict_next_stroke(strokes, boolean)
    print("---------------Predicted Stroke---------------")
    return json.dumps({"data": responseTurn, "transformation": "shift"})


if __name__ == "__main__":
    api.run(port=8000)
