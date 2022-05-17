import streamlit as st
import pandas as pd
import numpy as pd
from ui_utils import get_dataset_subset

# st.title('Visualization')
# st.write('hello world')

def initialize_session_state():
 ## TODO initialize any session state needed - example below
#   if 'seen_image_indices_list' not in st.session_state:
#       st.session_state['seen_image_indices_list'] = []
    return


#initialize_session_state()

def reset_session_state():
    #TODO clear any session state on reset
    return

num_batches = 3
batch_size = 2
res = get_dataset_subset('wimbledon_2019_womens_final_halep_williams__fduc5bZx3ss',
['player_front','fast'],num_batches,batch_size)

for b in range(num_batches):
  for i in range(batch_size):
    st.image(res[b].get_frame_at(i).get_data())