import streamlit as st
import pandas as pd
import numpy as np
import argparse
import os

from ui_utils import Condition, get_dataset_subset, check_assertions

DATASET_PATH = './dataset/'

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', default=['./dataset/'],
                    help="Add dataset path")

try:
  args = parser.parse_args()
  DATASET_PATH = args.dataset[0]
except SystemExit as e:
  os._exit(e.code)


def initialize_session_state():
 ## TODO initialize any session state needed - example below
#   if 'seen_image_indices_list' not in st.session_state:
#       st.session_state['seen_image_indices_list'] = []
    return

initialize_session_state()

def reset_session_state():
    #TODO clear any session state on reset
    return

# 2 TABS layout
st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["Explore Dataset", "Detect Errors Using Assertions"]
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Explore Dataset"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Explore Dataset")
    active_tab = "Explore Dataset"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" target="_self" rel="noopener noreferrer" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""
st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# Helper for displaying results underneath tabs

if 'get_subset' not in st.session_state:
    st.session_state['get_subset'] = '--'
    
if 'find_errors' not in st.session_state:
    st.session_state['find_errors'] = '--'

def find_errors():
  st.session_state.find_errors = ''

def get_subset():
  st.session_state.get_subset = ''

# Content under Explore Dataset tab
if active_tab == "Explore Dataset":
  with st.sidebar:
    # mutliselect for 
    query_condition_list = st.multiselect('Search Filters', [c.name for c in Condition])
    num_batches = st.number_input('Number of batches', min_value=1, max_value=7, value=5)
    batch_size = st.number_input('Number of frames per batch', min_value=1, max_value=7, value=5)
    search_button = st.button("Search", on_click=get_subset)

# Content under asstertions tab
elif active_tab == "Detect Errors Using Assertions":
  with st.sidebar:
    num_batches = st.number_input('Number of assertions', min_value=1, max_value=10, value=1)
    search_button = st.button("Find errors", on_click=find_errors)

else:
    st.error("Something has gone terribly wrong.")

# Check if search button has been clicked
if st.session_state.get_subset != '--':
  if (query_condition_list):
    ## LAYOUT - 2 cols
    cols = st.columns(batch_size)

    # Get data
    res, _ = get_dataset_subset(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
      query_condition_list,num_batches,batch_size, True)
    
    # Plot data
    for b in range(num_batches):
      for i in range(batch_size):
        cols[i].image(res[b].get_frame_at(i).get_data(), use_column_width=True)


# Check if find errors button has been clicked
if st.session_state.find_errors != '--':
  res, dataset = get_dataset_subset(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
    ['fast', 'player_back'],5, 10, False)

  assertions = [{'keypoints': ['right_elbow','right_shoulder','right_wrist', 'right_shoulder'], 'type': 'spatial', 'attributes': ['above', 'above']}, \
              {'keypoints': ['left_shoulder','right_shoulder','left_knee', 'right_knee', 'left_hip', 'right_hip'], 'type': 'spatial', 'attributes': ['left', 'left', 'left']}, \
              {'keypoints': ['left_shoulder','right_shoulder','left_knee', 'right_knee', 'left_hip', 'right_hip'], 'type': 'spatial', 'attributes': ['right', 'right', 'right']}, \
              {'keypoints': ['left_elbow','right_elbow','left_wrist','right_wrist'], 'type': 'spatial', 'attributes': [('smaller', 0.05),('smaller', 0.15)]}, \
              {'keypoints': ['left_ankle','right_ankle','left_knee','right_knee'], 'type': 'spatial', 'attributes': [('smaller', 0.05),('smaller', 0.15)]}, \
              {'keypoints': ['head_top','head_bottom'], 'type': 'spatial', 'attributes': [('smaller', 0.25)]}, \
              {'keypoints': ['right_wrist'], 'type': 'temporal', 'attributes': [0.3]},
              {'keypoints': ['left_wrist'], 'type': 'temporal', 'attributes': [0.3]}]

  errors, frames = check_assertions(DATASET_PATH + 'wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss', dataset, res, assertions, True)

  if errors is not None:
    st.dataframe(errors)
    if frames is not None:
      for f in frames:
        st.image(f.get_data())
