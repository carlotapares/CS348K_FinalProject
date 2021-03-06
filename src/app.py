from flask import Flask, render_template, request
from flask_cors import CORS
import numpy as np
import json
import sys
sys.path.append('./')
sys.path.append('./static/dataset/')
from data_utils import get_prediction, PoseTrack_Keypoint_Pairs
from ui_utils import get_dataset_subset, check_assertions
from matplotlib import colors


FILENAME = 'SNMOT-061'
FILE_EXTENSION = '.jpg'
DATASET_PATH = './static/dataset/' + FILENAME + '/'

dataset_json = json.load(open(DATASET_PATH + FILENAME + '.pose.json', 'r'))

app = Flask(__name__,static_folder='static',template_folder='templates')
CORS(app)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/search', methods = ['POST'])
def search():
  content = request.get_json(silent=True)
  res = get_dataset_subset(dataset_json, DATASET_PATH + FILENAME,
          content['checkbox'],int(content['batches']),int(content['frames']), False)

  frames_ = []
  keypoints_ = []
  bbox_ = []
  asst_ = []

  if res == None or len(res) == 0:
    data_ = {"error": True, "images": [], "keypoints": [], "bbox": []}
    return json.dumps(data_)

  for b in range(len(res)):
    for f in range(res[b].length()):
      frame_num = res[b].get_frame_at(f).get_prediction().get_real_frame_number()
      keypoints = res[b].get_frame_at(f).get_prediction().get_keypoints()
      bbox = res[b].get_frame_at(f).get_prediction().get_bbox()
      person = res[b].get_frame_at(f).get_prediction().get_person()

      frame_num_rel = res[b].get_frame_at(f).get_prediction().get_relative_frame_number()

      pred_1 = get_prediction(dataset_json, max(0,frame_num_rel - 1), person)
      if pred_1 == None:
        pred_1 = res[b].get_frame_at(f).get_prediction()
      keypoints_1 = pred_1.get_keypoints()
      bbox_1 = pred_1.get_bbox()
      prev = pred_1.get_real_frame_number()

      pred_3 = get_prediction(dataset_json, min(len(dataset_json['person'])-1,frame_num_rel + 1), person)
      if pred_3 == None:
        pred_3 = res[b].get_frame_at(f).get_prediction()
      keypoints_3 = pred_3.get_keypoints()
      bbox_3 = pred_3.get_bbox()
      next = pred_3.get_real_frame_number()

      frames_.append([formated_frame(prev+1), formated_frame(frame_num+1), formated_frame(next + 1)])
      keypoints_.append([formated_keypoints(keypoints_1, bbox_1),
                        formated_keypoints(keypoints, bbox), 
                        formated_keypoints(keypoints_3, bbox_3)])
      bbox_.append([bbox_1, bbox, bbox_3])
      asst_.append('')

  data_ = {"error": False, "images": frames_, "keypoints": keypoints_, "bbox": bbox_, "asst_names": asst_}
  return json.dumps(data_)

def formated_frame(frame_num):
  return FILENAME + '/frames/thumb' + str(frame_num).zfill(4) + FILE_EXTENSION

def formated_keypoints(keypoints, bbox):
  x,y,_,_ = list(map(int, bbox))
  kp_plot = []
  for joint_pair in PoseTrack_Keypoint_Pairs:
    ind_1, ind_2, color = joint_pair
    x1, y1 = keypoints[ind_1].position()
    x2, y2 = keypoints[ind_2].position()

    kp_plot.append((int(x1-x), int(y1-y), int(x2-x), int(y2-y), np.round(colors.to_rgba(color),2).tolist()))
  return kp_plot

@app.route('/check', methods = ['POST'])
def check():
  content = request.get_json(silent=True)
  assertions = []
  data_ = {"error": True, "images": [], "keypoints": [], "bbox": []}

  if not content["assertions"] or content["assertions"][0] != '[' or content["assertions"][-1] != ']':
    return json.dumps(data_)

  asst = content['assertions'][1:].replace("}]","},").replace("'",'"').split("},")[:-1]
  if len(asst) == 0 or asst[0] == "{":
    return json.dumps(data_)

  for a in asst:
    a = a + "}"
    try:
      j = json.loads(a)
      assertions.append(j)
    except Exception as e:
      print(e)
      print("Error in ", a)
      data_ = {"error": True, "images": [], "keypoints": [], "bbox": []}
      return json.dumps(data_)

  res = get_dataset_subset(dataset_json, DATASET_PATH + FILENAME,
          content['checkbox'],0,0, False)

  errors, _ = check_assertions(DATASET_PATH + FILENAME, dataset_json, res, assertions, False)

  #errors.to_csv('errors.csv', index=False)

  if errors is None:
    data_ = {"error": False, "images": [], "keypoints": [], "bbox": []}
    return json.dumps(data_)

  frames_ = []
  keypoints_ = []
  bbox_ = []
  asst_ = []

  fn = errors['relative_frame_number'].tolist()
  pl = errors['person'].tolist()
  asst = errors['assertion'].tolist()

  for ii, f in enumerate(fn):
    frame = get_prediction(dataset_json, f, pl[ii])
    keypoints = frame.get_keypoints()
    bbox = frame.get_bbox()
    person = frame.get_person()

    pred_1 = get_prediction(dataset_json, max(0,f - 1), person)
    if pred_1 == None:
      pred_1 = frame
    keypoints_1 = pred_1.get_keypoints()
    bbox_1 = pred_1.get_bbox()
    prev = pred_1.get_real_frame_number()

    pred_3 = get_prediction(dataset_json, min(len(dataset_json['person'])-1,f + 1), person)
    if pred_3 == None:
      pred_3 = frame
    keypoints_3 = pred_3.get_keypoints()
    bbox_3 = pred_3.get_bbox()
    next = pred_3.get_real_frame_number()

    frames_.append([formated_frame(prev+1), formated_frame(frame.get_real_frame_number()+1), formated_frame(next + 1)])
    keypoints_.append([formated_keypoints(keypoints_1, bbox_1),
                      formated_keypoints(keypoints, bbox), 
                      formated_keypoints(keypoints_3, bbox_3)])
    bbox_.append([bbox_1, bbox, bbox_3])
    asst_.append(asst[ii])

  data_ = {"error" : False, "images": frames_, "keypoints": keypoints_, "bbox": bbox_, "asst_names": asst_}
  return json.dumps(data_)