import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.ticker import FuncFormatter
from statsmodels.stats import weightstats as stests
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import norm
from dotenv import load_dotenv
from datetime import datetime
from Vanguard_backend import load_data, get_summary, clear_search, get_individual, confirmation_rate, navigation_time, drop_rate, bounce_rate, error_rate
 
def main():
    st.set_page_config(
    page_title="Vanguard Ltda",
    layout="wide",
    initial_sidebar_state="expanded")
 
    # Load data 
    data = load_data()
    
    # Interactive widgets
    st.sidebar.header('Controls')

    if 'search_id' not in st.session_state:
        st.session_state['search_id'] = ''

    search_id = st.sidebar.text_input('Enter Client ID to search:', value=st.session_state['search_id'], key='search_id')

    if st.sidebar.button('Clear Search', on_click=clear_search):
        pass

    min_age, max_age = st.sidebar.slider(
        "Select Age Range",
        min_value=int(data['clnt_age'].min()),
        max_value=int(data['clnt_age'].max()),
        value=(int(data['clnt_age'].min()), int(data['clnt_age'].max())),
        step=1)

    group_options_variation = ['All', 'Control', 'Test']
    selected_group_variation = st.sidebar.selectbox('Select Group', group_options_variation)

    group_options_gender = ['All', 'Male', 'Female','Unknown']
    selected_group_gender = st.sidebar.selectbox('Select Group', group_options_gender)

    # Filter by rating
    filtered_data = data[(data['clnt_age'] >= min_age) & (data['clnt_age'] <= max_age)]
 
    if selected_group_variation == 'Control':
        filtered_data = filtered_data[filtered_data['Variation'] == 'Control']
    elif selected_group_variation == 'Test':
        filtered_data = filtered_data[filtered_data['Variation'] == 'Test']

    if selected_group_gender == 'Male':
        filtered_data = filtered_data[filtered_data['gendr'] == 'M']
    elif selected_group_gender == 'Female':
        filtered_data = filtered_data[filtered_data['gendr'] == 'F']
    elif selected_group_gender == 'Unknown':
        filtered_data = filtered_data[filtered_data['gendr'] == 'U']

    if search_id:
        # Attempt to convert the input to an integer (assuming client_id is an integer)
        try:
            search_id_int = int(search_id)
            individual_df = data[data['client_id'] == search_id_int]
            if not individual_df.empty:  # Ensure DataFrame is not empty
                result_search = get_individual(individual_df)
                with st.expander("Client Statistics"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("ID", search_id)
                        st.metric("Age", f"{result_search['Age'][0]} years")
                        st.metric("Tenure", f"{result_search['Tenure'][0]} years")
                        st.metric("Gender", result_search['Gender'][0])
                        st.metric("Balance", f"${result_search['Balance'][0]:.2f}")
                    
                    with col2:
                        st.text("Steps Summary")
                        for column in result_search.columns:
                            value = result_search[column].iloc[0]
                            if column == 'Step Amount':
                                for step, count in value.items():
                                    st.text(f"{step}: {count}")
                        st.metric("Group Variation", result_search['Group'][0])
                        last_access_str = result_search['Last Access'][0]
                        last_access_datetime = datetime.strptime(last_access_str, '%Y-%m-%d %H:%M:%S')
                        st.metric("Last Use", last_access_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                st.write('No client found with that ID.')
        except ValueError:
            st.write('Please enter a valid integer ID.')

    st.write("### Summary Statistics")
    updated_summary = get_summary(filtered_data)

    # Use columns to display each statistic in its own 'card'
    col1, col2, col3, col4, col5, col6 = st.columns(6)  # Adjust the number of columns based on your summary statistics

    with col1:
        clients_count = updated_summary['Clients'][0]
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #add8e6; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block;
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Total Clients</h2>
            <h1>{clients_count}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        average_age = updated_summary['Average Age'][0]
        average_age_rounded = int(round(average_age, 0))
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #235e71; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block; 
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Avarage Age</h2>
            <h1>{average_age_rounded}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        average_tenure = updated_summary['Average Tenure'][0]
        average_tenure_rounded = int(round(average_tenure, 0))
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #235e71; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block; 
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Avarage Tenure</h2>
            <h1>{average_tenure_rounded}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        percentage_control = updated_summary['Percentage Control'][0]
        percentage_control_rounded = int(round(percentage_control, 0))
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #235e71; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block; 
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Control Group (%)</h2>
            <h1>{percentage_control_rounded}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        percentage_test = updated_summary['Percentage Test'][0]
        percentage_test_rounded = int(round(percentage_test, 0))
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #235e71; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block; 
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Test Group (%)</h2>
            <h1>{percentage_test_rounded}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col6:

        error_rate_value = error_rate(filtered_data)
        rounded_error_rate_value = round(error_rate_value * 100)
        st.markdown(f"""
        <style>
        .metric {{
            background-color: #235e71; 
            border-radius: 5px; 
            padding: 0.5em; 
            color: black; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            margin: 5px; 
            text-align: center;
            display: inline-block; 
        }}

        .metric h2 {{
            margin-top: 0;
            font-size: 1rem; 
            font-weight: 400; 
        }}

        .metric h1 {{
            margin: 0.25em 0; 
            font-size: 1.75rem;
            font-weight: 500;
        }}
        </style>
        <div class="metric">
            <h2>Avarage Error Rate (%)</h2>
            <h1>{rounded_error_rate_value}</h1>
        </div>
        """, unsafe_allow_html=True)   

    # Display graph
    col1_graph, col2_graph = st.columns(2) 
    with col1_graph:
        confirmation_rate(filtered_data)
    with col2_graph:
        bounce_rate(filtered_data)

    col1_graph2, col2_graph2 = st.columns(2) 
    with col1_graph2:
        drop_rate(filtered_data)
    with col2_graph2:
        navigation_time(filtered_data)

if __name__ == '__main__':
    main()