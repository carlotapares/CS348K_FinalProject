<div align="center">
<br>
<h3>
Assertions for error detection in human pose estimation
</h3>
<h4>
Carlota Parés-Morlans & Liana Patel
</h4>
<p>
<i>A project for CS348K:  Visual Computing Systems, Spring 2022, Stanford University, CA.</i>
</p>
</div>

In this work, we design and implement a system that allows developers to (i) explore and (ii) easily find errors
on human pose labels using high-level abstractions. Specifically, we built a system that provides the subject matter expert a set of (i) data exploration and (ii) data error detection
tools to quickly detect labeling errors.

![](https://github.com/carlotapares/CS348K_FinalProject/blob/main/src/static/demo/exploration.png)
![](https://github.com/carlotapares/CS348K_FinalProject/blob/main/src/static/demo/assertions.png)
----
## Assertions DSL

```python
[{'keypoints': ['right_elbow','right_shoulder','right_wrist', 'right_shoulder'], 'type': 'spatial', 'attributes': ['above', 'above']},
{'keypoints': ['left_elbow','right_elbow','left_wrist','right_wrist'], 'type': 'spatial', 'attributes': [['smaller', 0.05],['smaller', 0.15]]},
{'keypoints': ['right_wrist'], 'type': 'temporal', 'attributes': [0.3]}]
```
- Keypoints: ```'head_bottom','head_top','left_shoulder','right_shoulder','left_elbow','right_elbow','left_wrist','right_wrist',
'left_hip','right_hip','left_knee','right_knee','left_ankle','right_ankle' ```
- Types: 'spatial', 'temporal'
- Position conditions: 'above', 'below', 'left', 'right'
- Size conditions: ['smaller', <bbox height %>], ['bigger', <bbox height %>]
- Temporal conditions: [<bbox height %>]

----

## Getting Started

### Installation

Clone this repository into a directory.

```bash
git clone https://github.com/carlotapares/CS348K_FinalProject.git
cd CS348K_FinalProject
```

Install dependencies.
```bash
pip install -r requirements.txt
```

### Dataset

For the system to work, the ``` .json ``` file containing the estimated human poses needs to be placed in the following path ```./src/static/dataset/[dataset_name]/[dataset_name].pose.json```. Note the extension ```.pose.json```.
Regarding the video frames, the system requires a folder that contains all the frames extracted from the original video ```./src/static/dataset/[dataset_name]/frames/```. The system expects frames to be named as ```thumb[frame_number].[jpg|png]```. The frame number must have at least 4 digits. For instance, the image that corresponds to frame 1 would be named as ```thumb0001.png```.
The dataset name needs to be specified in the variable [FILENAME](https://github.com/carlotapares/CS348K_FinalProject/blob/9d5abce697b09ddf2aff02eb95833ce492b6f7c5/src/app.py#L13) from the file [app.py](https://github.com/carlotapares/CS348K_FinalProject/blob/9d5abce697b09ddf2aff02eb95833ce492b6f7c5/src/app.py#L13). The file extension needs to be specified in the variable [FILE_EXTENSION](https://github.com/carlotapares/CS348K_FinalProject/blob/9d5abce697b09ddf2aff02eb95833ce492b6f7c5/src/app.py#L14) from the file [app.py](https://github.com/carlotapares/CS348K_FinalProject/blob/9d5abce697b09ddf2aff02eb95833ce492b6f7c5/src/app.py#L14)
### Bring up the server

The main file for this project is ```./src/app.py```. To run it, after requirements have been installed using ```pip install -r requirements.txt```, please run the following command.
```bash
cd src
flask run
```

The interface is accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Important notes about the dataset
The system expects a json that follows the following format:
```json
{
  "person": [[
      876,
      [
        {
          "score": 0.8828125,
          "xywh": [
            1260,
            679,
            58,
            161
          ],
          "pose": [[
              [
                1290,
                693,
                0.7042282819747925
              ],
              [
                1291,
                703,
                0.7967766523361206
              ],
              [
                1286,
                682,
                0.8929957151412964
              ],
              [
                1277,
                790,
                8.28044605255127
              ],
              [
                1250,
                694,
                0.13085046410560608
              ],
              [
                1279,
                712,
                0.7459417581558228
              ],
              [
                1304,
                711,
                0.7732439041137695
              ],
              [
                1272,
                733,
                0.6717427372932434
              ],
              [
                1309,
                738,
                0.7777752876281738
              ],
              [
                1268,
                737,
                0.5357966423034668
              ],
              [
                1313,
                756,
                0.7257556915283203
              ],
              [
                1281,
                759,
                0.5836173892021179
              ],
              [
                1301,
                759,
                0.5823633670806885
              ],
              [
                1276,
                791,
                0.7135104537010193
              ],
              [
                1303,
                794,
                0.6818797588348389
              ],
              [
                1270,
                823,
                0.699542224407196
              ],
              [
                1306,
                827,
                0.8392575979232788
              ]
            ]
          ]
        }
      ]
    ]
  ]
}
```
Where ```876``` is the frame number for poses included in this element.
Note that the order of the keypoints inside the ```pose``` array follow [COCO Keypoint Ordering]([https://github.com/carlotapares/CS348K_FinalProject/blob/main/src/data_utils.py#:~:text=%5D-,PoseTrack_COCO_Keypoint_Ordering,-%3D%20%5B](https://github.com/carlotapares/CS348K_FinalProject/blob/10a45951f2e53046a95c2547d0a144017e2ed49c/src/data_utils.py#L24)).
