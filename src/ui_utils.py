import io
import numpy as np
from enum import Enum
import os
from scipy.spatial import distance
import sys
sys.path.append('.')
sys.path.append('./src/dataset/')

from data_utils import Prediction, load_poses, get_prediction
from viz import get_image_data, get_prediction_vis

MIN_PIXEL_DIST_FAST_SPEED = 10 # 7 px displacement per frame

class Frame:
  def __init__(self, data: io.BytesIO, width: int, height: int) -> None:
    self.data_ = data
    self.width_ = width
    self.height_ = height
    self.channels_ = 'RGB'

  def width(self) -> int:
    return self.width_

  def height(self) -> int:
    return self.height_

  def channels(self) -> str:
    return self.channels_

  def get_data(self) -> io.BytesIO:
    return self.data_

class Batch:
  def __init__(self) -> None:
      self.len_ = 0
      self.frames_ = []

  def add_frame(self, frame : Frame) -> None:
    self.frames_.append(frame)
    self.len_ += 1

  def get_frame_at(self, pos: int) -> Frame:
    if pos < 0 or pos > (self.len_ - 1):
      raise RuntimeError('Incorrect position. Frame number should be between 0 and ' + str(self.len_ -1))
    return self.frames_[pos]

  def get_frames(self) -> 'list[Frame]':
    if len(self.frames_) == 0:
      raise RuntimeError('Empty frame list')

    return self.frames_

  def length(self) -> int:
    return self.len_

class Condition(Enum):
  PLAYER_FRONT = ('player_front', 'spatial')
  PLAYER_BACK = ('player_back', 'spatial')
  DIRECTION_RIGHT = ('right', 'temporal')
  DIRECTION_LEFT = ('left', 'temporal')
  SPEED_SLOW = ('slow', 'temporal')
  SPEED_FAST = ('fast', 'temporal')

  def __init__(self, name, ctype):
    self.name_ = name
    self.type_ = ctype

  @property
  def ctype(self):
    return self.type_

  @property
  def name(self):
    return self.name_

  @classmethod
  def exists(cls, name):
    return any(name == e.name for e in cls)

  @classmethod
  def from_name(cls, name):
    for item in cls:
      if item.value[0] == name: return item

class ConditionChecker:
  def __init__(self) -> None:
    self.condition_ = None
    self.predictions_ = None

  def set_condition(self, condition: Condition) -> None:
    self.condition_ = condition

  def set_predictions(self, predictions: 'list[Prediction]') -> None:
    self.predictions_ = predictions

  def check(self):
    if self.condition_ == Condition.DIRECTION_RIGHT:
        return self.__check_direction_right()
    elif self.condition_ == Condition.DIRECTION_LEFT:
      return self.__check_direction_left()
    elif self.condition_ == Condition.SPEED_FAST:
      return self.__check_speed_fast()
    elif self.condition_ == Condition.SPEED_SLOW:
      return self.__check_speed_slow()
    elif self.condition_ == Condition.PLAYER_BACK:
      return self.__check_player_back()
    elif self.condition_ == Condition.PLAYER_FRONT:
      return self.__check_player_front()
    else:
      raise RuntimeError('Error. Non-existing condition')


  def __check_direction_right(self):
    prev_pos = self.predictions_[0].get_bbox()

    for i in range(1, len(self.predictions_)):
      next_pos = self.predictions_[i].get_bbox()

      if prev_pos[0] > next_pos[0]:
        return False 

      prev_pos = next_pos

  def __check_direction_left(self):
    prev_pos = self.predictions_[0].get_bbox()

    for i in range(1, len(self.predictions_)):
      next_pos = self.predictions_[i].get_bbox()

      if prev_pos[0] < next_pos[0]:
        return False 

      prev_pos = next_pos

  def __check_speed_fast(self):
    prev_pos = self.predictions_[0].get_bbox()
    dist = 0

    for i in range(1, len(self.predictions_)):
      next_pos = self.predictions_[i].get_bbox()
      dist += distance.cdist([prev_pos[0:2]], [next_pos[0:2]], 'euclidean')[0][0]

    dist /= len(self.predictions_)

    if dist >= MIN_PIXEL_DIST_FAST_SPEED:
      return True

    return False

  def __check_speed_slow(self):
    prev_pos = self.predictions_[0].get_bbox()
    dist = 0

    for i in range(1, len(self.predictions_)):
      next_pos = self.predictions_[i].get_bbox()
      dist += distance.cdist([prev_pos[0:2]], [next_pos[0:2]], 'euclidean')[0][0]

    dist /= len(self.predictions_)

    if dist < MIN_PIXEL_DIST_FAST_SPEED:
      return True
      
    return False

  def __check_player_back(self):
    return self.predictions_[0].get_player() == 'back'

  def __check_player_front(self):
    return self.predictions_[0].get_player() == 'front'

class Predicate:
  def __init__(self, filename: str, conditions: 'list[Condition]', num_batches: int, batch_size: int) -> None:
    self.filename_ = filename
    self.conditions_ = conditions
    self.num_batches_ = num_batches
    self.batch_size_ = batch_size
    self.dataset_ = None
    self.path_ = './dataset/'
    self.time_between_batches_ = 3
    self.FPS_ = 25

  def __load_dataset(self) -> None:
    files = os.listdir(self.path_)
    if self.filename_ + '.mp4' not in files:
      raise RuntimeError('Check '+ self.filename_ + '.mp4 file exists in path ' + self.path_)
    if self.filename_ + '.pose.json' not in files:
      raise RuntimeError('Check '+ self.filename_ + '.pose.json file exists in path ' + self.path_)
    
    self.dataset_ = load_poses(self.path_ + self.filename_ + '.pose.json')
  
  def run(self) -> 'list[Batch]':
    self.__load_dataset()
    out = []
    lb = 0

    while len(out) < self.num_batches_:
      start = self.time_between_batches_* self.FPS_ * lb
      end = start + self.batch_size_
      batch_frames = np.arange(start, end, dtype=int)
      if start > len(self.dataset_['person']) -1 or end > len(self.dataset_['person']) -1:
        raise('Could not find the number of frames selected. Check batches and batch size.')
     
      lb += 1

      frames_front = []
      frames_back = []
 
      for f in batch_frames:
        pp = get_prediction(self.dataset_, f, "front")
        if pp:
          frames_front.append(pp)
        pp = get_prediction(self.dataset_, f, "back")
        if pp:
          frames_back.append(pp)

      if frames_front:
        cond_checker_front = ConditionChecker()
        cond_checker_front.set_predictions(frames_front)

        for condition in self.conditions_:
          cond_checker_front.set_condition(condition)
          res = cond_checker_front.check()
          if res == False:
            frames_front = None
            break

        # If frames passed conditions, get visualization
        if frames_front:
          batch = Batch()
          for f in frames_front:
            img = get_image_data(self.path_ + self.filename_, f.get_frame_number())
            data, w, h = get_prediction_vis(f, img)
            frame = Frame(data, w, h)
            batch.add_frame(frame)
          out.append(batch)

      if frames_back:
        cond_checker_back = ConditionChecker()
        cond_checker_back.set_predictions(frames_back)

        for condition in self.conditions_:
          cond_checker_back.set_condition(condition)
          res = cond_checker_back.check()
          if res == False:
            frames_back = None
            break
      
        # If frames passed conditions, get visualization
        if frames_back:
          batch = Batch()
          for f in frames_back:
            img = get_image_data(self.path_ + self.filename_, f.get_frame_number())
            data, w, h = get_prediction_vis(f, img)
            frame = Frame(data, w, h)
            batch.add_frame(frame)
          out.append(batch)

    return out

def get_dataset_subset(filename: str, tags: 'list[str]', num_batches: int, batch_size: int) -> 'list[Batch]':
  conditions = []

  for tag in tags:
    if Condition.exists(tag):
      c = Condition.from_name(tag)
      if c.ctype == 'temporal' and batch_size <= 1:
        raise RuntimeError('Batch size has to be bigger than 1 for temporal conditions.')
      conditions.append(c)
    else:
      raise RuntimeError('Tag ' + tag + ' is not supported')

  p = Predicate(filename, conditions, num_batches, batch_size)
  return p.run()