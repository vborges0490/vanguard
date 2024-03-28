import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your dataset
df = pd.read_csv('data.csv')

# Streamlit app title
st.title('My Streamlit App')

# Dropdown menu for field selection
selected_field = st.selectbox('Select Field', df.columns)

# Display a graph based on the selected field
# Adjust this part according to what graph you want to display and how your data is structured
# For demonstration, we're plotting the distribution of the selected field using a histogram
if st.button('Show Graph'):
    fig, ax = plt.subplots()
    df[selected_field].hist(ax=ax)
    st.pyplot(fig)