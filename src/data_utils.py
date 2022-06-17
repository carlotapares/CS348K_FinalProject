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
    self.person_ = None
    self.real_frame_number_ = -1
    self.relative_frame_number_ = -1

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

  def get_person(self) -> str:
    return self.person_

  def set_person(self, person: str) -> None:
    self.person_ = person

  def get_real_frame_number(self) -> int:
    return self.real_frame_number_

  def set_real_frame_number(self, frame_number: int) -> None:
    self.real_frame_number_ = frame_number

  def get_relative_frame_number(self) -> int:
    return self.relative_frame_number_

  def set_relative_frame_number(self, frame_number: int) -> None:
    self.relative_frame_number_ = frame_number

def get_bounding_box(file: dict, frame: int, person: int) -> tuple([int, int]):
  if person >= len(file['person'][frame][1]): return None
  return file['person'][frame][1][person]['xywh']

def get_keypoints(file: dict, frame: int, person: int) -> 'list[Keypoint]':
  if person >= len(file['person'][frame][1]): return None
  keypoints =  file['person'][frame][1][person]['pose'][0]
  out = []

  for i, k in enumerate(keypoints):
    out.append(Keypoint(k[0],k[1], PoseTrack_COCO_Keypoint_Ordering[i]))

  return out

def get_real_frame_number(file: dict, frame: int) -> int:
  return file['person'][frame][0]

def get_prediction(file: dict, frame: int, person: int) -> Prediction:
  keypoints = get_keypoints(file, frame, person)
  bbox = get_bounding_box(file, frame, person)

  if not keypoints or not bbox:
    return None

  p = Prediction()
  p.set_bbox(bbox)
  p.set_keypoints(keypoints)
  p.set_person(person)
  p.set_relative_frame_number(frame)
  p.set_real_frame_number(get_real_frame_number(file, frame))
  return p
