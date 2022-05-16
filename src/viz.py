import numpy as np
import cv2
import io
import matplotlib.pyplot as plt
from data_utils import Prediction, PoseTrack_Keypoint_Pairs

def get_image_data(path: str, frame: int) -> np.array:
  cap = cv2.VideoCapture(path + '.mp4')
  cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
  ret, frame = cap.read()

  if ret:
      return np.asarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
  else:
      raise RuntimeError('No frame obtained.')

def get_prediction_vis(pred: Prediction, image: np.array) -> io.BytesIO:
  keypoints = pred.get_keypoints()
  x,y,w,h = list(map(int, pred.get_bbox()))
  
  plt.imshow(image[y:y+h,x:x+w,:], alpha=0.6)
  for joint_pair in PoseTrack_Keypoint_Pairs:
    ind_1, ind_2, color = joint_pair
    x1, y1, _ = keypoints[ind_1]
    x2, y2, _ = keypoints[ind_2]
            
    plt.plot([x1-x, x2-x], [y1-y, y2-y], c=color, linewidth=2)

  b = io.BytesIO()
  plt.savefig(b, format='png',dpi=200)
  plt.close()

  return b, plt.gcf().get_size_inches() * 200
