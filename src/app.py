import streamlit as st
import pandas as pd
import numpy as pd
from ui_utils import Condition, get_dataset_subset, check_assertions

# HARD-CODED PARAMS
num_batches = 3 # number of search results to return to user  
# batch_size = 1 # number of frames to return per batch


def initialize_session_state():
 ## TODO initialize any session state needed - example below
#   if 'seen_image_indices_list' not in st.session_state:
#       st.session_state['seen_image_indices_list'] = []
    return

#initialize_session_state()

def reset_session_state():
    #TODO clear any session state on reset
    return



# USER SEARCH INPUT IN SIDE BAR
'''with st.sidebar:
  # mutliselect for 
  query_condition_list = st.multiselect('Search Filters', [c.name for c in Condition])
  batch_size = st.number_input('Number frames per clip', min_value=1, max_value=7, value=5)

## LAYOUT - 2 cols
cols = st.columns(batch_size)'''


# RETURNED RESULTS
'''if (query_condition_list):
  st.write(query_condition_list)
  res, _ = get_dataset_subset('wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
    query_condition_list,num_batches,batch_size, True)

  st.write('Returned ' + str(len(res)) + ' results.')

  for b in range(num_batches):
    for i in range(batch_size):
      cols[i].image(res[b].get_frame_at(i).get_data(), use_column_width=True)'''

res, dataset = get_dataset_subset('wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
    ['fast','player_back'],5, 20, False)

#assertions = [{'keypoints': ['right_elbow','right_shoulder','right_wrist', 'right_shoulder'], 'type': 'spatial', 'attributes': ['above', 'below']}]
assertions = [{'keypoints': ['left_knee','right_knee', 'left_ankle','right_ankle',], 'type': 'spatial', 'attributes': ['left','left']}, \
              {'keypoints': ['right_wrist','right_shoulder'], 'type': 'spatial', 'attributes': ['bigger', 0.1]}]

errors, frames = check_assertions(dataset, res, assertions, True)

print(errors)
if errors is not None:
  st.dataframe(errors)
  for f in frames:
    st.image(f.get_data())


  # res = get_dataset_subset('wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
  #   ['player_front','fast'],num_batches,batch_size)

  # for b in range(num_batches):
  #   for i in range(batch_size):
  #     st.image(res[b].get_frame_at(i).get_data())



  # ## SECTION 1 - SEARCH SECTION INPUTS
  # query_input = st.text_input('What are you looking for?')
  # search_method = st.selectbox('search method', options=METHODS)
  # search_button = st.button("Search", on_click=submit_search, 
  #                             kwargs={'query_text': query_input, 
  #                                     'search_method':search_method})
  # reset_button = st.button("Reset Search", on_click=reset_session_state) # reset saved_images

  # #st.selectbox('ImageNet Class Label', class_labels)
  # st.write('----------------------------')
  # st.write('Create New Label')
  # ## SECTION 2 - CREATE NEW LABEL SECTION INPUTS
  # query_class_list = st.multiselect('ImageNet Class Label', class_labels)
  # new_label = st.text_input('New Class Name:')
  # checkbox_keys = []
  # submit_button = st.button("Submit", on_click=submit_create_label, kwargs={'checkbox_keys':checkbox_keys, 'new_label':new_label})


  





