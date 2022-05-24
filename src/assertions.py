import pandas as pd
from enum import Enum
from scipy.spatial import distance

from data_utils import Prediction, PoseTrack_COCO_Keypoint_Ordering, get_prediction

class PositionCondition(Enum):
  ABOVE = "above",
  BELOW = "below",
  RIGHT = "right",
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
  BIGGER = "bigger",
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
  def __init__(self, assertion: Assertion, prediction: Prediction):
    self.assertion_ = assertion
    self.prediction_ = prediction

  def get_prediction(self) -> Prediction:
    return self.prediction_

  def get_assertion(self) -> Assertion:
    return self.assertion_

  def get_data_as_df(self) -> pd.DataFrame:
    d = {"assertion" : self.assertion_}
    for k,v in self.prediction_.get_keypoints.items():
      d[k] = v.position()
    d['frame_number'] = self.prediction_.get_frame_number()

    return pd.DataFrame(d, index=[0])

class AssertionChecker:
    def __init__(self, dataset) -> None:
      self.assertions_ = {}
      self.errors_ = []
      self.dataset_ = dataset

    def register_assertion(self, assertion: Assertion) -> None:
        if assertion.name() is None:
            name = 'asst_{}'.format(len(self.assertions))
            assertion.set_name(name)
            
        if assertion.name() in self.assertions:
            raise RuntimeError('Attempting to add two assertions with the same name!')

        self.assertions_[assertion.name()] = assertion

    def retrieve_errors(self) -> pd.DataFrame:
        errors = []
        
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
      keypoint_positions = []

      if not all(kp in PoseTrack_COCO_Keypoint_Ordering for kp in kps):
        raise RuntimeError('Incorrect keypoints: ' + '-'.join(kps))

      for p in input:
        k = p.get_keypoints()
        for kp in kps:
          keypoint_positions.append(k[kp].position())

        # Relative position between keypoints
        if atts[0] is PositionCondition and len(kps) == len(atts) - 1:
          for j, c in enumerate(atts):
            if c is PositionCondition.ABOVE:
              if keypoint_positions[j][1] < keypoint_positions[j+1][1]:
                errors.append(LabellingError(asst, p))
              
            elif c is PositionCondition.BELOW:
              if keypoint_positions[j][1] > keypoint_positions[j+1][1]:
                errors.append(LabellingError(asst, p))

            elif c is PositionCondition.LEFT:
              if keypoint_positions[j][0] > keypoint_positions[j+1][0]:
                errors.append(LabellingError(asst, p))

            elif c is PositionCondition.RIGHT:
              if keypoint_positions[j][0] < keypoint_positions[j+1][0]:
                errors.append(LabellingError(asst, p))
            else:
              raise RuntimeError('Incorrect condition: ' + c.name + ' for assertion: ' + asst.name())

        # Size of a joint relative to the height of the bounding box
        elif len(kps) == 2 and len(atts) == 2 and atts[0] is SizeCondition and type(atts[1]) in [float, int]:
            bbox_height = p.get_bbox()[-1]
            if atts[0] is SizeCondition.BIGGER:
              if abs(distance.cdist([[keypoint_positions[0]]], [[keypoint_positions[1]]], 'euclidean')[0][0]) < atts[1]*bbox_height:
                errors.append(LabellingError(asst, p))
            else:
              if abs(distance.cdist([[keypoint_positions[0]]], [[keypoint_positions[1]]], 'euclidean')[0][0]) > atts[1]*bbox_height:
                errors.append(LabellingError(asst, p))
          
        else:
          raise RuntimeError('Wrong number of keypoints and attributes for assertion: ' + asst.name())

      return errors

    def __check_temporal_assertion(self, asst: Assertion, input: 'list[Prediction]') -> 'list[LabellingError]':
      fn = asst.function()
      atts = fn.attributes()
      kps = fn.keypoints()
      errors = []

      if not all(kp in PoseTrack_COCO_Keypoint_Ordering for kp in kps):
        raise RuntimeError('Incorrect keypoints: ' + '-'.join(kps))

      if len(kps) == 1 and len(atts) == 1 and type(atts[0]) in [float,int]:

        for p1 in input:
          p2 = get_prediction(self.dataset_, p1.get_frame_number()+1, p1.get_player())
          x1,y1 = p1.keypoints()[kps[0]].position()
          x2,y2 = p2.keypoints()[kps[0]].position()

          if abs(distance.cdist([[x1,y1]], [[x2,y2]], 'euclidean')[0][0]) > atts[0]:
            errors.append(LabellingError(asst, p1))

      else:
        raise RuntimeError('Incorrect parameters for assertion: ' + asst.name())

      return errors







