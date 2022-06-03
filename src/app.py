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

DATASET_PATH = './static/dataset/'

dataset_json = json.load(open(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss.pose.json', 'r'))

app = Flask(__name__,static_folder='static',template_folder='templates')
CORS(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/search', methods = ['POST'])
def search():
  content = request.get_json(silent=True)
  print(content)
  res = get_dataset_subset(dataset_json, DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
          content['checkbox'],int(content['batches']),int(content['frames']), False)

  frames_ = []
  keypoints_ = []
  bbox_ = []

  for b in range(len(res)):
    for f in range(res[b].length()):
      frame_num = res[b].get_frame_at(f).get_prediction().get_real_frame_number()
      keypoints = res[b].get_frame_at(f).get_prediction().get_keypoints()
      bbox = res[b].get_frame_at(f).get_prediction().get_bbox()
      player = res[b].get_frame_at(f).get_prediction().get_player()

      frame_num_rel = res[b].get_frame_at(f).get_prediction().get_relative_frame_number()

      pred_1 = get_prediction(dataset_json, max(0,frame_num_rel - 1), player)
      keypoints_1 = pred_1.get_keypoints()
      bbox_1 = pred_1.get_bbox()
      prev = pred_1.get_real_frame_number()

      pred_3 = get_prediction(dataset_json, min(len(dataset_json['person'])-1,frame_num_rel + 1), player)
      keypoints_3 = pred_3.get_keypoints()
      bbox_3 = pred_3.get_bbox()
      next = pred_3.get_real_frame_number()

      frames_.append([prev+1, frame_num+1, next + 1])
      keypoints_.append([formated_keypoints(keypoints_1, bbox_1),
                        formated_keypoints(keypoints, bbox), 
                        formated_keypoints(keypoints_3, bbox_3)])
      bbox_.append([bbox_1, bbox, bbox_3])

  data_ = {"images": frames_, "keypoints": keypoints_, "bbox": bbox_}
  #print(data_)
  return json.dumps(data_)

def formated_keypoints(keypoints, bbox):
  x,y,_,_ = list(map(int, bbox))
  kp_plot = []
  for joint_pair in PoseTrack_Keypoint_Pairs:
    ind_1, ind_2, color = joint_pair
    x1, y1 = keypoints[ind_1].position()
    x2, y2 = keypoints[ind_2].position()

    kp_plot.append((int(x1-x), int(y1-y), int(x2-x), int(y2-y), np.round(colors.to_rgba(color),2).tolist()))
  return kp_plot

# res = get_dataset_subset(dataset_json, DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
#     [],300, 70, False)

# assertions = [{'keypoints': ['right_elbow','right_shoulder','right_wrist', 'right_shoulder'], 'type': 'spatial', 'attributes': ['above', 'above']}, \
#             {'keypoints': ['left_shoulder','right_shoulder','left_knee', 'right_knee', 'left_hip', 'right_hip'], 'type': 'spatial', 'attributes': ['left', 'left', 'left']}, \
#             {'keypoints': ['left_shoulder','right_shoulder','left_knee', 'right_knee', 'left_hip', 'right_hip'], 'type': 'spatial', 'attributes': ['right', 'right', 'right']}, \
#             {'keypoints': ['left_elbow','right_elbow','left_wrist','right_wrist'], 'type': 'spatial', 'attributes': [('smaller', 0.05),('smaller', 0.15)]}, \
#             {'keypoints': ['left_ankle','right_ankle','left_knee','right_knee'], 'type': 'spatial', 'attributes': [('smaller', 0.05),('smaller', 0.15)]}, \
#             {'keypoints': ['head_top','head_bottom'], 'type': 'spatial', 'attributes': [('smaller', 0.25)]}, \
#             {'keypoints': ['right_wrist'], 'type': 'temporal', 'attributes': [0.3]},
#             {'keypoints': ['left_wrist'], 'type': 'temporal', 'attributes': [0.3]}]

# errors, frames = check_assertions(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss', dataset_json, res, assertions, False)
