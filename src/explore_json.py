import json
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

DATASET_PATH = './static/dataset/'

dataset_json = json.load(open(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss.pose.json', 'r'))
frame_num = 6872

for f in dataset_json['person']:
  if f[0] == frame_num:
    bb = f[1][1]['xywh']
    x,y,w,h = list(map(int, bb))
    im = Image.open('./static/dataset/frames/thumb' + str(frame_num).zfill(4) + '.png')
    im = np.asarray(im)
    plt.figure()
    plt.subplot(1,2,1)
    plt.imshow(im[y:y+h,x:x+w,:],alpha=1)
    plt.subplot(1,2,2)
    plt.imshow(im)
    plt.show()
    break


{'keypoints': ['right_elbow','right_shoulder','right_wrist', 'right_shoulder'], 'type': 'spatial', 'attributes': ['above', 'above']}
{'keypoints': ['left_elbow','right_elbow','left_wrist','right_wrist'], 'type': 'spatial', 'attributes': [['smaller', 0.05],['smaller', 0.15]]}
{'keypoints': ['left_ankle','right_ankle','left_knee','right_knee'], 'type': 'spatial', 'attributes': [['smaller', 0.05],['smaller', 0.15]]}
{'keypoints': ['head_top','head_bottom'], 'type': 'spatial', 'attributes': [['smaller', 0.25]]}
{'keypoints': ['right_wrist'], 'type': 'temporal', 'attributes': [0.3]}
{'keypoints': ['left_wrist'], 'type': 'temporal', 'attributes': [0.3]}
{'keypoints': ['left_hip','left_ankle'], 'type': 'spatial', 'attributes': ['above']}
{'keypoints': ['right_hip','right_ankle'], 'type': 'spatial', 'attributes': ['above']}
{'keypoints': ['left_hip','left_knee'], 'type': 'spatial', 'attributes': ['above']}
{'keypoints': ['right_hip','right_knee'], 'type': 'spatial', 'attributes': ['above']}
