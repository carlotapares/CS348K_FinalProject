import json
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

DATASET_PATH = './static/dataset/'

dataset_json = json.load(open(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss.pose.json', 'r'))
frame_num = 20671

for f in dataset_json['person']:
  if f[0] == frame_num:
    bb = f[1][1]['xywh']
    x,y,w,h = list(map(int, bb))
    im = Image.open('./static/dataset/frames/thumb' + str(frame_num).zfill(4) + '.png')
    im = np.asarray(im)
    plt.figure()
    plt.subplot(1,2,1)
    plt.imshow(im[y:y+h,x:x+w,:],alpha=0.6)
    plt.subplot(1,2,2)
    plt.imshow(im)
    plt.show()
    break