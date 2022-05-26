import io
import numpy as np
from enum import Enum
import os
from scipy.spatial import distance
import streamlit as st
import pandas as pd

from data_utils import Prediction, load_poses, get_prediction
from assertions import Assertion, AssertionChecker, AssertionFunction
from viz import get_image_data, get_prediction_vis, get_image_data_from_video

MIN_PIXEL_DIST_FAST_SPEED = 10 # 10 px displacement per frame

class Frame:
  def __init__(self, data: io.BytesIO, width: int, height: int, prediction: Prediction) -> None:
    self.data_ = data
    self.width_ = width
    self.height_ = height
    self.channels_ = 'RGB'
    self.prediction_ = prediction

  def width(self) -> int:
    return self.width_

  def height(self) -> int:
    return self.height_

  def channels(self) -> str:
    return self.channels_

  def get_data(self) -> io.BytesIO:
    return self.data_

  def get_prediction(self) -> Prediction:
    return self.prediction_

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
      mid_prev = [[prev_pos[0] + prev_pos[2]//2, prev_pos[1] + prev_pos[3]//2]]
      mid_next = [[next_pos[0] + next_pos[2]//2, next_pos[1] + next_pos[3]//2]]
      dist += distance.cdist(mid_prev, mid_next, 'euclidean')[0][0]

    dist /= len(self.predictions_)

    if dist >= MIN_PIXEL_DIST_FAST_SPEED:
      return True

    return False

  def __check_speed_slow(self):
    prev_pos = self.predictions_[0].get_bbox()
    dist = 0

    for i in range(1, len(self.predictions_)):
      next_pos = self.predictions_[i].get_bbox()
      mid_prev = [[prev_pos[0] + prev_pos[2]//2, prev_pos[1] + prev_pos[3]//2]]
      mid_next = [[next_pos[0] + next_pos[2]//2, next_pos[1] + next_pos[3]//2]]
      dist += distance.cdist(mid_prev, mid_next, 'euclidean')[0][0]

    dist /= len(self.predictions_)

    if dist < MIN_PIXEL_DIST_FAST_SPEED:
      return True
      
    return False

  def __check_player_back(self):
    return self.predictions_[0].get_player() == 'back'

  def __check_player_front(self):
    return self.predictions_[0].get_player() == 'front'

class Predicate:
  def __init__(self, filename: str, conditions: 'list[Condition]', num_batches: int, batch_size: int, include_display=False) -> None:
    self.filename_ = filename
    self.path_ = '/'.join(filename.split('/')[:-1])
    self.conditions_ = conditions
    self.num_batches_ = num_batches
    self.batch_size_ = batch_size
    self.dataset_ = None
    self.time_between_batches_ = 3
    self.FPS_ = 25
    self.include_display_ = include_display

  def get_dataset(self) -> dict:
    if not self.dataset_:
      raise RuntimeError('Returning an empty dataset')
    return self.dataset_
  
  def run(self) -> 'list[Batch]':
    self.dataset_ = load_poses(self.filename_ + '.pose.json')
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

        
        # If frames passed conditions
        if frames_front and len(out) < self.num_batches_:
          batch = Batch()
          for f in frames_front:
            if self.include_display_:
              # img = get_image_data(self.path_, f.get_real_frame_number()+1)
              img = get_image_data_from_video(self.path_ + self.filename_, f.get_real_frame_number())
              data, w, h = get_prediction_vis(f, img)
              frame = Frame(data, w, h, f)
            else:
              frame = Frame(None, -1, -1, f)
            batch.add_frame(frame)
          out.append(batch)
        

      if frames_back and len(out) < self.num_batches_:
        cond_checker_back = ConditionChecker()
        cond_checker_back.set_predictions(frames_back)

        for condition in self.conditions_:
          cond_checker_back.set_condition(condition)
          res = cond_checker_back.check()
          if res == False:
            frames_back = None
            break
      
        # If frames passed conditions
        if frames_back:
          batch = Batch()
          for f in frames_back:
            if self.include_display_:
              # img = get_image_data(self.path_, f.get_real_frame_number()+1)
              img = get_image_data_from_video(self.path_ + self.filename_, f.get_real_frame_number())
              data, w, h = get_prediction_vis(f, img)
              frame = Frame(data, w, h, f)
            else:
              frame = Frame(None, -1, -1, f)
            batch.add_frame(frame)
          out.append(batch)

    return out

def get_dataset_subset(filename: str, tags: 'list[str]', num_batches: int, batch_size: int, include_display=False) -> tuple(['list[Batch]', dict]):
  conditions = []

  for tag in tags:
    if Condition.exists(tag):
      c = Condition.from_name(tag)
      if c.ctype == 'temporal' and batch_size <= 1:
        raise RuntimeError('Batch size has to be bigger than 1 for temporal conditions.')
      conditions.append(c)
    else:
      raise RuntimeError('Tag ' + tag + ' is not supported')

  p = Predicate(filename, conditions, num_batches, batch_size, include_display)
  result = p.run()
  return result, p.get_dataset()

def check_assertions(path: str, dataset: dict, input: 'list[Batch]', assertions = 'list[dict]', include_display=False) -> tuple([pd.DataFrame, 'list[Frame]']):
  a = AssertionChecker(dataset)
  for asst in assertions:
    a.register_assertion(Assertion(AssertionFunction(asst['keypoints'], asst['type'], asst['attributes'])))

  preds = []
  for b in input:
    for f in b.get_frames():
      preds.append(f.get_prediction())

  a.check(preds)
  errors = a.retrieve_errors()

  if errors is None:
    return None, None

  if include_display:
    frames = []
    frame_num = errors.loc[:,'frame_number'].tolist()
    pred_idx = errors.loc[:,'prediction_idx'].tolist()
    
    for ii, f in enumerate(frame_num):
      # img = get_image_data(path, f+1)
      img = get_image_data_from_video(path, f)
      data, w, h = get_prediction_vis(preds[pred_idx[ii]], img)
      frame = Frame(data, w, h, preds[pred_idx[ii]])
      frames.append(frame)

    return errors, frames

  else:
    return errors, None

  




