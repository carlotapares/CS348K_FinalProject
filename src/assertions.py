import pandas as pd
from enum import Enum
from scipy.spatial import distance
import numpy as np
from data_utils import Prediction, PoseTrack_COCO_Keypoint_Ordering, get_prediction

class PositionCondition(Enum):
  ABOVE = "above"
  BELOW = "below"
  RIGHT = "right"
  LEFT = "left"

  def __init__(self, name):
    self.name_ = name

  @property
  def name(self):
    return self.name_

  @classmethod
  def exists(cls, name):
    return any(name == e.name for e in cls)

  @classmethod
  def from_name(cls, name):
    for item in cls:
      if item.value == name: return item

class SizeCondition(Enum):
  BIGGER = "bigger"
  SMALLER = "smaller"

  def __init__(self, name):
    self.name_ = name

  @property
  def name(self):
    return self.name_

  @classmethod
  def exists(cls, name):
    return any(name == e.name for e in cls)

  @classmethod
  def from_name(cls, name):
    for item in cls:
      if item.value == name: return item

class AssertionFunction:
  def __init__(self, keypoints: 'list[str]', atype: str, attributes: 'list[str]'):
    self.keypoints_ = keypoints
    self.type_ = atype
    self.attributes_ = attributes

  def type(self) -> str:
    return self.type_ 
  
  def keypoints(self) -> 'list[str]':
    return self.keypoints_

  def attributes(self) -> 'list':
    return self.attributes_

class Assertion:
  def __init__(self, fn: AssertionFunction) -> None:
    self.name_ = None
    self.fn_ = fn

  def name(self) -> str:
    return self.name_

  def set_name(self, name: str) -> None:
    self.name_ = name

  def function(self) -> AssertionFunction:
    return self.fn_

  def set_function(self, fn: AssertionFunction) -> None:
    self.fn_ = fn

class LabellingError:
  def __init__(self, assertion: Assertion, prediction: Prediction, pred_idx: int):
    self.assertion_ = assertion
    self.prediction_ = prediction
    self.pred_idx_ = pred_idx

  def get_prediction(self) -> Prediction:
    return self.prediction_

  def get_prediction_indx(self) -> Prediction:
    return self.pred_idx_

  def get_assertion(self) -> Assertion:
    return self.assertion_

  def get_data_as_df(self) -> pd.DataFrame:
    d = {"assertion" : self.assertion_.name()}
    for k,v in self.prediction_.get_keypoints().items():
      d[k] = '(' + str(v.position()[0]) + ',' + str(v.position()[1]) + ')'
    d['frame_number'] = self.prediction_.get_real_frame_number()
    d['relative_frame_number'] = self.prediction_.get_relative_frame_number()
    d['prediction_idx'] = self.get_prediction_indx()
    d['player'] = self.prediction_.get_player()

    return pd.DataFrame(d, index=[0])

class AssertionChecker:
    def __init__(self, dataset) -> None:
      self.assertions_ = {}
      self.errors_ = []
      self.dataset_ = dataset

    def register_assertion(self, assertion: Assertion) -> None:
        if assertion.name() is None:
            name = 'asst_{}'.format(len(self.assertions_))
            assertion.set_name(name)
            
        if assertion.name() in self.assertions_:
            raise RuntimeError('Attempting to add two assertions with the same name!')

        self.assertions_[assertion.name()] = assertion

    def retrieve_errors(self) -> pd.DataFrame:
        errors = []

        if not self.errors_:
          return None
        
        for error in self.errors_:
          errors.append(error.get_data_as_df())

        return pd.concat(errors, ignore_index=True)

    def clear_errors(self) -> None:
        self.errors_ = []

    def check(self, input) -> None:
      for name, asst in self.assertions_.items():
        if asst.function().type() == 'spatial':
          err = self.__check_spatial_assertion(asst, input)
        elif asst.function().type() == 'temporal':
          err = self.__check_temporal_assertion(asst, input)
        else:
          raise RuntimeError('Wrong function type for assertion: ' + name)

        if err:
          self.errors_.extend(err)

    def __check_spatial_assertion(self, asst: Assertion, input: 'list[Prediction]') -> 'list[LabellingError]':
      fn = asst.function()
      atts = fn.attributes()
      kps = fn.keypoints()
      errors = []

      if not all(kp in PoseTrack_COCO_Keypoint_Ordering for kp in kps):
        raise RuntimeError('Incorrect keypoints: ' + '-'.join(kps))

      for ii, p in enumerate(input):
        keypoint_positions = []
        k = p.get_keypoints()
        for kp in kps:
          keypoint_positions.append(k[kp].position())

        bbox_height = p.get_bbox()[-1]

        # Relative position between keypoints
        if PositionCondition.exists(atts[0]) and len(kps) == len(atts) * 2 and len(kps) % 2 == 0:
          last_true = -1

          for j, c in enumerate(atts):
            cd = PositionCondition.from_name(c)
            x_diff = keypoint_positions[j*2][0] - keypoint_positions[j*2+1][0]
            y_diff = keypoint_positions[j*2][1] - keypoint_positions[j*2+1][1]
            margin = 0.001*bbox_height

            if cd is PositionCondition.ABOVE:
              if y_diff < -margin:
                if (j - last_true) == 1: last_true = j
              elif abs(y_diff) < margin: last_true = len(atts)
              
            elif cd is PositionCondition.BELOW:
              if y_diff > margin:
                if (j - last_true) == 1: last_true = j
              elif abs(y_diff) < margin: last_true = len(atts)

            elif cd is PositionCondition.LEFT:
              if x_diff < -margin:
                if (j - last_true) == 1: last_true = j
              elif abs(x_diff) < margin: last_true = len(atts)

            elif cd is PositionCondition.RIGHT:
              if x_diff > margin:
                if (j - last_true) == 1: last_true = j
              elif abs(x_diff) < margin: last_true = len(atts)
            else:
              raise RuntimeError('Incorrect condition: ' + c + ' for assertion: ' + asst.name())

          if last_true == len(atts) - 2:
            errors.append(LabellingError(asst, p, ii))

        # Relative distance between keypoints wrt the height of the bounding box
        elif len(atts[0]) == 2 and SizeCondition.exists(atts[0][0]) and len(kps) == len(atts) * 2 and len(kps) % 2 == 0:
          last_true = -1

          for j, c in enumerate(atts):
            cd = SizeCondition.from_name(c[0])
            if cd is SizeCondition.BIGGER and type(c[1]) in [int, float]:
              if abs(distance.cdist([keypoint_positions[2*j]], [keypoint_positions[2*j+1]], 'euclidean')[0][0]) > c[1]*bbox_height:
                if (j - last_true) == 1: last_true = j
            elif cd is SizeCondition.SMALLER and type(c[1]) in [int, float]:
              if abs(distance.cdist([keypoint_positions[2*j]], [keypoint_positions[2*j+1]], 'euclidean')[0][0]) < c[1]*bbox_height:
                if (j - last_true) == 1: last_true = j
            else:
              raise RuntimeError('Incorrect condition: ' + str(c) + ' for assertion: ' + asst.name())

          if last_true == len(atts) - 2:
            errors.append(LabellingError(asst, p, ii))
          
        else:
          raise RuntimeError('Wrong params for assertion: ' + asst.name())

      return errors

    def __check_temporal_assertion(self, asst: Assertion, input: 'list[Prediction]') -> 'list[LabellingError]':
      fn = asst.function()
      atts = fn.attributes()
      kps = fn.keypoints()
      errors = []

      if not all(kp in PoseTrack_COCO_Keypoint_Ordering for kp in kps):
        raise RuntimeError('Incorrect keypoints: ' + '-'.join(kps))

      if len(kps) == 1 and len(atts) == 1 and type(atts[0]) in [float,int]:

        for ii, p1 in enumerate(input):
          dist = []
          x1,y1 = p1.get_keypoints()[kps[0]].position()
          # 4 frame observation
          for jj in range(-2, 2):
            if jj == 0:
              continue
            p2 = get_prediction(self.dataset_, max(0, p1.get_relative_frame_number()+jj), p1.get_player())
            if p2:
              x2,y2 = p2.get_keypoints()[kps[0]].position()
              dist.append(abs(distance.cdist([[x1,y1]], [[x2,y2]], 'euclidean')[0][0]))

          if len(dist) > 0 and np.min(dist) > atts[0]*p1.get_bbox()[3]:
            errors.append(LabellingError(asst, p1, ii))

      else:
        raise RuntimeError('Incorrect parameters for assertion: ' + asst.name())

      return errors