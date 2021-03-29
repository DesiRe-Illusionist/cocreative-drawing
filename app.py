from flask import Flask, request, json
from flask_cors import CORS, cross_origin
#from scipy.stats import bernoulli
import random
import numpy as np
import os,base64
import contour_test
from PIL import Image, ImageDraw

api = Flask(__name__)
cors = CORS(api)

@api.route('/draw', methods=['POST'])
def reactToDraw():
  strokes = request.get_json().get("data")
  width = request.get_json().get("width")
  height = request.get_json().get("height")

  ######################################
  #origin image processing, turn image to file blank.png
  img_base=request.get_json().get("file")
  str_img="data:image/png;base64,"
  img_base=img_base.replace(str_img,"",1)
  imgdata=base64.b64decode(img_base)
  file_img=open('blank.png','wb')
  file_img.write(imgdata)
  file_img.close()
  #try using contour
  max_thresh=255
  thresh=200
  print("original")
  dist=contour_test.thresh_callback(thresh,"blank.png")
  ######################################
  
  #rotate = bernoulli.rvs(p=0.5, size=1)
  rotateOptions = [90, 180, 270]
  scaleOptions = [0.5, 2.0]
  rotateDeg = random.choice(rotateOptions)
  scale = random.choice(scaleOptions)
  transOptions=['shift','rotate','reflect','scale','shadow','verthatch']
  transformation=random.choice(transOptions)
  
  #origin method of responseTurn
#   responseTurn=[]
#   for stroke in strokes:
#     responseStroke = []
#     midstroke=stroke[round(len(stroke)/2)-1]
#     midX = midstroke[0]
#     midY = midstroke[1]
#     xshift=random.randint(-50,50)
#     yshift=random.randint(-50,50)
#     for point in stroke:
#         xin=point[0]
#         yin=point[1]
#         if transformation=='reflect':
#             responseX = width - xin
#             responseY = height - yin
#         elif transformation=='rotate':
#             responseX = np.cos(rotateDeg) * (xin - midX) - np.sin(rotateDeg) * (yin - midY) + midX
#             responseY = np.sin(rotateDeg) * (xin - midX) + np.cos(rotateDeg) * (yin - midY) + midY
#         elif transformation=='shift':
#             responseX = xin + xshift
#             responseY = yin + yshift
#         elif transformation=='scale':
#             if scale<1:
#                 responseX = xin * scale + midX*scale
#                 responseY = yin * scale + midY*scale
#             elif scale>=1:
#                 responseX = xin * scale - midX
#                 responseY = yin * scale - midY
#         elif transformation == 'shadow' or transformation == 'verthatch':
#                 #handle this one in p5
#                 responseX = xin
#                 responseY = yin
#         responseStroke.append([responseX, responseY])
#     responseTurn.append(responseStroke)


  ######################################
  #calculating new strokes
  ######################################
  responseTurn=[]
  #trans_Opt=['shift','rotate','reflect','scale']
  refl_turn=[]
  rotate_turn=[]
  shift_turn=[]
  scale_turn=[]
  for stroke in strokes:
    refl_stroke = []
    rotate_stroke=[]
    shift_stroke=[]
    scale_stroke=[]
    midstroke=stroke[round(len(stroke)/2)-1]
    midX = midstroke[0]
    midY = midstroke[1]
    xshift=random.randint(-50,50)
    yshift=random.randint(-50,50)
    for point in stroke:
        xin=point[0]
        yin=point[1]
        #reflect
        X_refl = width - xin
        Y_refl = height - yin
        #rotate
        X_rotate = np.cos(rotateDeg) * (xin - midX) - np.sin(rotateDeg) * (yin - midY) + midX
        Y_rotate = np.sin(rotateDeg) * (xin - midX) + np.cos(rotateDeg) * (yin - midY) + midY
        #shift
        X_shift = xin + xshift
        Y_shift = yin + yshift
        #scale
        if scale<1:
            X_scale = xin * scale + midX*scale
            Y_scale = yin * scale + midY*scale
        elif scale>=1:
            X_scale = xin * scale - midX
            Y_scale = yin * scale - midY
        # elif transformation == 'shadow' or transformation == 'verthatch':
        #         #handle this one in p5
        #         responseX = xin
        #         responseY = yin
        refl_stroke.append([X_refl, Y_refl])
        rotate_stroke.append([X_rotate, Y_rotate])
        shift_stroke.append([X_shift, Y_shift])
        scale_stroke.append([X_scale, Y_scale])
    refl_turn.append(refl_stroke)
    rotate_turn.append(rotate_stroke)
    shift_turn.append(shift_stroke)
    scale_turn.append(scale_stroke)

  #reflect
  with Image.open("blank.png") as im:
    draw=ImageDraw.Draw(im)
    for resp_stroke in refl_turn:
        processed_stroke=[]
        for i in range(len(resp_stroke)):
            processed_stroke.append((resp_stroke[i][0]*2, resp_stroke[i][1]*2))
        draw.line(processed_stroke,fill=(0,0,0),width=10,joint="curve")
    im.save("reflect.png")
    print("\n reflect")
    dist_test=contour_test.thresh_callback(thresh,"reflect.png")
    if dist_test<dist:
        responseTurn=refl_turn
        dist=dist_test
  #rotate
  with Image.open("blank.png") as im:
    draw=ImageDraw.Draw(im)
    for resp_stroke in rotate_turn:
        processed_stroke=[]
        for i in range(len(resp_stroke)):
            processed_stroke.append((resp_stroke[i][0]*2, resp_stroke[i][1]*2))
        draw.line(processed_stroke,fill=(0,0,0),width=10,joint="curve")
    im.save("rotate.png")
    print("\n rotate")
    dist_test=contour_test.thresh_callback(thresh,"rotate.png")
    if dist_test<dist:
        responseTurn=rotate_turn
        dist=dist_test
  #shift
  with Image.open("blank.png") as im:
    draw=ImageDraw.Draw(im)
    for resp_stroke in shift_turn:
        processed_stroke=[]
        for i in range(len(resp_stroke)):
            processed_stroke.append((resp_stroke[i][0]*2, resp_stroke[i][1]*2))
        draw.line(processed_stroke,fill=(0,0,0),width=10,joint="curve")
    im.save("shift.png")
    print("\n shift")
    dist_test=contour_test.thresh_callback(thresh,"shift.png")
    if dist_test<dist:
        responseTurn=shift_turn
        dist=dist_test
  #scale
  with Image.open("blank.png") as im:
    draw=ImageDraw.Draw(im)
    for resp_stroke in scale_turn:
        processed_stroke=[]
        for i in range(len(resp_stroke)):
            processed_stroke.append((resp_stroke[i][0]*2, resp_stroke[i][1]*2))
        draw.line(processed_stroke,fill=(0,0,0),width=10,joint="curve")
    im.save("scale.png")
    print("\n scale")
    dist_test=contour_test.thresh_callback(thresh,"scale.png")
    if dist_test<dist:
        responseTurn=scale_turn
        dist=dist_test
  print(dist)


  return json.dumps({"data": responseTurn,"transformation": transformation})

if __name__ == '__main__':
    api.run(port=8000)
