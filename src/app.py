import streamlit as st
import pandas as pd
import numpy as pd

# st.title('Visualization')
# st.write('hello world')

def initialize_session_state():
 ## TODO initialize any session state needed - example below
#   if 'seen_image_indices_list' not in st.session_state:
#       st.session_state['seen_image_indices_list'] = []
    return


initialize_session_state()

def reset_session_state():
    #TODO clear any session state on reset
    return

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df