import numpy as np
import cv2
import io
import matplotlib.pyplot as plt
from data_utils import Prediction, PoseTrack_Keypoint_Pairs
from PIL import Image

def get_image_data_from_video(path: str, frame: int) -> np.array:
  cap = cv2.VideoCapture(path + '.mp4')
  cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
  ret, f = cap.read()
  if ret:
      return f
  else:
      raise RuntimeError('No frame obtained.')

def get_image_data(path: str, frame: int) -> np.array:
  img_path = path + '/frames/thumb' + '{0:04d}'.format(frame+1) + '.png'
  img = Image.open(img_path)
  return np.asarray(img)

def get_prediction_vis(pred: Prediction, image: np.array) -> tuple([io.BytesIO,int,int]):
  keypoints = pred.get_keypoints()
  x,y,w,h = list(map(int, pred.get_bbox()))

  #plt.imshow(cv2.cvtColor(image[y:y+h,x:x+w,:], cv2.COLOR_BGR2RGB),alpha=0.6)
  plt.imshow(image[y:y+h,x:x+w,:],alpha=0.6)

  for joint_pair in PoseTrack_Keypoint_Pairs:
    ind_1, ind_2, color = joint_pair
    x1, y1 = keypoints[ind_1].position()
    x2, y2 = keypoints[ind_2].position()
            
    plt.plot([x1-x, x2-x], [y1-y, y2-y], c=color, linewidth=2)

  b = io.BytesIO()
  plt.savefig(b, format='png',dpi=200)
  plt.close()

  w, h =plt.gcf().get_size_inches()

  return b, w * 200, h*200
