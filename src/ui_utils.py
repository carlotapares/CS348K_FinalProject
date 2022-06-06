import io
import numpy as np
from enum import Enum
from scipy.spatial import distance
import pandas as pd

from data_utils import Prediction, get_prediction
from assertions import Assertion, AssertionChecker, AssertionFunction
from viz import get_image_data, get_prediction_vis, get_image_data_from_video

MIN_DIST_FAST_SPEED = 0.05 # 5% of the bbox height displacement per frame

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
  def __init__(self, dataset) -> None:
    self.condition_ = None
    self.predictions_ = None
    self.dataset_ = dataset

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
    out = []
    for pred in self.predictions_:
      prev = get_prediction(self.dataset_, pred.get_relative_frame_number() - 1, pred.get_player())
      next = get_prediction(self.dataset_, pred.get_relative_frame_number() + 1, pred.get_player())

      if prev == None or next == None:
        continue
      
      if pred.get_player() == 'back':
        if prev.get_bbox()[0] > pred.get_bbox()[0] and pred.get_bbox()[0] > next.get_bbox()[0]:
          out.append(pred)
      else:
        if prev.get_bbox()[0] < pred.get_bbox()[0] and pred.get_bbox()[0] < next.get_bbox()[0]:
          out.append(pred)

    return out

  def __check_direction_left(self):
    out = []
    for pred in self.predictions_:
      prev = get_prediction(self.dataset_, pred.get_relative_frame_number() - 1, pred.get_player())
      next = get_prediction(self.dataset_, pred.get_relative_frame_number() + 1, pred.get_player())

      if prev == None or next == None:
        continue
      
      if pred.get_player() == 'back':
        if prev.get_bbox()[0] < pred.get_bbox()[0] and pred.get_bbox()[0] < next.get_bbox()[0]:
          out.append(pred)
      else:
        if prev.get_bbox()[0] > pred.get_bbox()[0] and pred.get_bbox()[0] > next.get_bbox()[0]:
          out.append(pred)

    return out

  def __check_speed_fast(self):
    out = []
    for pred in self.predictions_:
      pred_bbox = pred.get_bbox()
      prev = get_prediction(self.dataset_, pred.get_relative_frame_number() - 1, pred.get_player())
      next = get_prediction(self.dataset_, pred.get_relative_frame_number() + 1, pred.get_player())

      if prev == None or next == None:
        continue

      prev = prev.get_bbox()
      next = next.get_bbox()

      dist1 = abs(distance.cdist([[pred_bbox[0] + pred_bbox[2]//2, pred_bbox[1] + pred_bbox[3]//2]], [[prev[0] + prev[2]//2, prev[1] + prev[3]//2]], 'euclidean')[0][0])
      dist3 = abs(distance.cdist([[pred_bbox[0] + pred_bbox[2]//2, pred_bbox[1] + pred_bbox[3]//2]], [[next[0] + next[2]//2, next[1] + next[3]//2]], 'euclidean')[0][0])
      
      if dist1 > MIN_DIST_FAST_SPEED * pred_bbox[3] and dist3 > MIN_DIST_FAST_SPEED * pred_bbox[3]:
        out.append(pred)

    return out

  def __check_speed_slow(self):
    out = []
    for pred in self.predictions_:
      pred_bbox = pred.get_bbox()
      prev = get_prediction(self.dataset_, pred.get_relative_frame_number() - 1, pred.get_player())
      next = get_prediction(self.dataset_, pred.get_relative_frame_number() + 1, pred.get_player())

      if prev == None or next == None:
        continue

      prev = prev.get_bbox()
      next = next.get_bbox()

      dist1 = abs(distance.cdist([[pred_bbox[0] + pred_bbox[2]//2, pred_bbox[1] + pred_bbox[3]//2]], [[prev[0] + prev[2]//2, prev[1] + prev[3]//2]], 'euclidean')[0][0])
      dist3 = abs(distance.cdist([[pred_bbox[0] + pred_bbox[2]//2, pred_bbox[1] + pred_bbox[3]//2]], [[next[0] + next[2]//2, next[1] + next[3]//2]], 'euclidean')[0][0])
      
      if dist1 < MIN_DIST_FAST_SPEED * pred_bbox[3] and dist3 < MIN_DIST_FAST_SPEED * pred_bbox[3]:
        out.append(pred)

    return out

  def __check_player_back(self):
    out = []
    for pred in self.predictions_:
      if pred.get_player() == 'back':
        out.append(pred)
    return out

  def __check_player_front(self):
    out = []
    for pred in self.predictions_:
      if pred.get_player() == 'front':
        out.append(pred)
    return out

class Predicate:
  def __init__(self, dataset: dict, filename: str, conditions: 'list[Condition]', num_batches: int, batch_size: int, include_display=False) -> None:
    self.path_ = '/'.join(filename.split('/')[:-1]) + '/'
    self.filename_ = filename.split('/')[-1]
    self.conditions_ = conditions
    self.dataset_ = dataset
    self.time_between_batches_ = 3
    self.FPS_ = 25
    self.include_display_ = include_display
    self.num_batches_ = num_batches if num_batches != 0 else len(dataset['person'])*2
    self.batch_size_ = batch_size if batch_size != 0 else self.time_between_batches_* self.FPS_
  
  def run(self) -> 'list[Batch]':
    out = []
    lb = 0

    while len(out) < self.num_batches_:
      start = self.time_between_batches_* self.FPS_ * lb
      end = start + self.batch_size_
      batch_frames = np.arange(start, end, dtype=int)
      if start > len(self.dataset_['person']) -1 or end > len(self.dataset_['person']) -1:
        break
     
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
        cond_checker_front = ConditionChecker(self.dataset_)
        cond_checker_front.set_predictions(frames_front)

        for condition in self.conditions_:
          cond_checker_front.set_condition(condition)
          frames_front = cond_checker_front.check()
          cond_checker_front.set_predictions(frames_front)
          if frames_front is None:
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
        cond_checker_back = ConditionChecker(self.dataset_)
        cond_checker_back.set_predictions(frames_back)
        
        for condition in self.conditions_:
          cond_checker_back.set_condition(condition)
          frames_back = cond_checker_back.check()
          cond_checker_back.set_predictions(frames_back)
          if frames_back is None:
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

def get_dataset_subset(dataset_json: dict, filename: str, tags: 'list[str]', num_batches: int, batch_size: int, include_display=False) -> tuple(['list[Batch]', dict]):
  conditions = []

  for tag in tags:
    if Condition.exists(tag):
      c = Condition.from_name(tag)
      conditions.append(c)
    else:
      raise RuntimeError('Tag ' + tag + ' is not supported')
  
  if Condition.PLAYER_BACK in conditions and Condition.PLAYER_FRONT in conditions:
    conditions.pop(conditions.index(Condition.PLAYER_BACK))
    conditions.pop(conditions.index(Condition.PLAYER_FRONT))

  if Condition.DIRECTION_RIGHT in conditions and Condition.DIRECTION_LEFT in conditions:
    conditions.pop(conditions.index(Condition.DIRECTION_LEFT))
    conditions.pop(conditions.index(Condition.DIRECTION_RIGHT))

  if Condition.SPEED_SLOW in conditions and Condition.SPEED_FAST in conditions:
    conditions.pop(conditions.index(Condition.SPEED_FAST))
    conditions.pop(conditions.index(Condition.SPEED_SLOW))

  p = Predicate(dataset_json, filename, conditions, num_batches, batch_size, include_display)
  result = p.run()
  return result

def check_assertions(path: str, dataset_json: dict, input: 'list[Batch]', assertions = 'list[dict]', include_display=False) -> tuple([pd.DataFrame, 'list[Frame]']):
  a = AssertionChecker(dataset_json)
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

  




