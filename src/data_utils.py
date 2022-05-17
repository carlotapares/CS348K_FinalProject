import json
import numpy as np

W = 1920
H = 1080

# Endpoint1 , Endpoint2 , line_color
PoseTrack_Keypoint_Pairs = [
    ['head_top', 'head_bottom', 'pink'],
    ['head_bottom', 'right_shoulder', 'yellow'],
    ['head_bottom', 'left_shoulder', 'yellow'],
    ['right_shoulder', 'right_elbow', 'blue'],
    ['right_elbow', 'right_wrist', 'blue'],
    ['left_shoulder', 'left_elbow', 'green'],
    ['left_elbow', 'left_wrist', 'green'],
    ['right_shoulder', 'right_hip', 'purple'],
    ['left_shoulder', 'left_hip', 'skyblue'],
    ['right_hip', 'right_knee', 'purple'],
    ['right_knee', 'right_ankle', 'purple'],
    ['left_hip', 'left_knee', 'skyblue'],
    ['left_knee', 'left_ankle', 'skyblue'],
]

PoseTrack_COCO_Keypoint_Ordering = [
    'nose',
    'head_bottom',
    'head_top',
    'left_ear',
    'right_ear',
    'left_shoulder',
    'right_shoulder',
    'left_elbow',
    'right_elbow',
    'left_wrist',
    'right_wrist',
    'left_hip',
    'right_hip',
    'left_knee',
    'right_knee',
    'left_ankle',
    'right_ankle',
]

class Keypoint:
  def __init__(self, x, y, name) -> None:
    self.position_ = (x,y)
    self.name_ = name

  def position(self) -> tuple([int,int]):
    return self.position_

  def name(self) -> str:
    return self.name_

class Prediction:
  def __init__(self) -> None:
    self.keypoints_ = {}
    self.bbox_ = None
    self.player_ = None
    self.frame_number_ = -1

  def get_keypoints(self) -> dict:
    if len(list(self.keypoints_.keys())) == 0:
      raise RuntimeError('Empty keypoints list')

    return self.keypoints_

  def set_keypoints(self, k: 'list[Keypoint]') -> None:
    for kp in k:
      self.keypoints_[kp.name()] = kp

  def get_bbox(self) -> 'list[int]':
    return self.bbox_

  def set_bbox(self, bbox) -> None:
    self.bbox_ = bbox

  def get_player(self) -> str:
    return self.player_

  def set_player(self, player: str) -> None:
    self.player_ = player

  def get_frame_number(self) -> int:
    return self.frame_number_

  def set_frame_number(self, frame_number: int) -> None:
    self.frame_number_ = frame_number
  
def load_poses(path: str) -> dict:
  return json.load(open(path, 'r'))

def get_player_list_position(file: dict, frame: int, player: str) -> int:
  if len(file['person'][frame][1]) != 2:
    return -1

  bbox1 = file['person'][frame][1][0]['xywh']
  bbox2 = file['person'][frame][1][1]['xywh']
  

  _,y1,_,_ = bbox1
  _,y2,_,_ = bbox2

  back_player = 0 if y1 < y2 else 1
  if player == 'back':
    return back_player
  else:
    return abs(back_player -1)

def get_bounding_box(file: dict, frame: int, player: str) -> tuple([int, int]):
  player_pos = get_player_list_position(file, frame, player)
  if player_pos == -1:
    return None
  return file['person'][frame][1][player_pos]['xywh']

def get_keypoints(file: dict, frame: int, player: str) -> 'list[Keypoint]':
  player_pos = get_player_list_position(file, frame, player)

  if player_pos == -1:
    return None

  keypoints =  file['person'][frame][1][player_pos]['pose'][0]
  out = []

  for i, k in enumerate(keypoints):
    out.append(Keypoint(k[0],k[1], PoseTrack_COCO_Keypoint_Ordering[i]))

  return out

def get_real_frame_number(file: dict, frame: int) -> int:
  return file['person'][frame][0]

def get_prediction(file: dict, frame: int, player: str) -> Prediction:
  keypoints = get_keypoints(file, frame, player)
  bbox = get_bounding_box(file, frame, player)

  if not keypoints or not bbox:
    return None

  p = Prediction()
  p.set_bbox(bbox)
  p.set_keypoints(keypoints)
  p.set_player(player)
  p.set_frame_number(get_real_frame_number(file, frame))
  return p



