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

load_dotenv()

directory = os.getenv('DIR')
df_final_data = os.getenv('CSV5')
plot_width, plot_height = 10, 6

def load_data():
    data = pd.read_csv(directory+df_final_data)
    return data

def clear_search():
    st.session_state.search_id = ''

def get_summary(data):
    summary = pd.DataFrame({
        'Clients': [data['client_id'].nunique()],
        'Average Age': [data['clnt_age'].mean()],
        'Average Tenure': [data['clnt_tenure_yr'].mean()],
        'Percentage Male': [data[data['gendr'] == 'M']['client_id'].nunique() / data['client_id'].nunique() * 100],
        'Percentage Female': [data[data['gendr'] == 'F']['client_id'].nunique() / data['client_id'].nunique() * 100],
        'Percentage Unknown': [data[data['gendr'] == 'U']['client_id'].nunique() / data['client_id'].nunique() * 100],
        'Percentage Control': [data[data['Variation'] == 'Control']['client_id'].nunique() / data['client_id'].nunique() * 100],
        'Percentage Test': [data[data['Variation'] == 'Test']['client_id'].nunique() / data['client_id'].nunique() * 100]
    })
    return summary
 
def get_individual(data):
    individual_summary = pd.DataFrame({
        'Step Amount': [data['process_step'].value_counts().to_dict()],
        'Group': [data['Variation'].iloc[0]],
        'Age': [data['clnt_age'].iloc[0]],
        'Tenure': [data['clnt_tenure_yr'].iloc[0]],
        'Gender': [data['gendr'].iloc[0]],
        'Balance': [data['bal'].sum() / len(data)],
        'Last Access': [data['date_time'].max()]
    })
    return individual_summary

def confirmation_rate(data):
    df_control_new = data[data["Variation"] == 'Control']
    df_test_new = data[data["Variation"] == 'Test']
    
    # Control Group Calculations
    if not df_control_new.empty:
        start_control = df_control_new.groupby('process_start')["visit_id"].nunique()
        start_control = start_control.iloc[1] if len(start_control) > 1 else np.nan
        confirm_control = df_control_new.groupby('process_confirm')["visit_id"].nunique()
        confirm_control = confirm_control.iloc[1] if len(confirm_control) > 1 else np.nan
        confirmation_rate_control = confirm_control / start_control if start_control > 0 else np.nan
    else:
        confirmation_rate_control = np.nan
    
    # Test Group Calculations
    if not df_test_new.empty:
        start_test = df_test_new.groupby('process_start')["visit_id"].nunique()
        start_test = start_test.iloc[1] if len(start_test) > 1 else np.nan
        confirm_test = df_test_new.groupby('process_confirm')["visit_id"].nunique()
        confirm_test = confirm_test.iloc[1] if len(confirm_test) > 1 else np.nan
        confirmation_rate_test = confirm_test / start_test if start_test > 0 else np.nan
    else:
        confirmation_rate_test = np.nan

    # Preparing data for plotting
    groups = ['Control', 'Test']
    rates = [confirmation_rate_control, confirmation_rate_test]
    colors = {'Control': 'blue', 'Test': 'green'}
    group_colors = [colors[group] for group in groups if not np.isnan(rates[groups.index(group)])]

    # Filter out NaN values for plotting
    groups = [group for group in groups if not np.isnan(rates[groups.index(group)])]
    rates = [rate for rate in rates if not np.isnan(rate)]
    
    text_color = 'white'  # Define a text color for visibility on dark background
    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
    ax.set_facecolor('none')  # Set the plot background to be transparent

    if groups:
        sns.barplot(x=groups, y=rates, palette=group_colors, ax=ax)
        ax.set_title('Confirmation Rates by Group', color=text_color)
        ax.set_ylabel('Confirmation Rate', color=text_color)
        ax.set_xlabel('Group', color=text_color)
        
        # Setting the y-axis to have a maximum of 100%
        ax.set_ylim(0, 1)  # Sets the y-axis to range from 0 to 1 (0% to 100%)
        
        # Format the y-ticks as percentages
        formatter = FuncFormatter(lambda y, _: f'{int(y*100)}%')
        ax.yaxis.set_major_formatter(formatter)

        # Set the tick colors
        ax.tick_params(axis='both', colors=text_color)

        # Customize grid to be visible on a dark background
        ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        
        # Displaying the plot in Streamlit
        st.pyplot(fig, transparent=True)
    else:
        st.write("Not enough data to display confirmation rates.")


def navigation_time(data):
    df_control_new = data[data["Variation"] == 'Control']
    df_test_new = data[data["Variation"] == 'Test']

    step_avgtime_control = df_control_new['start_time'].sum() / df_control_new['process_start-step1'].sum()
    step_avgtime_test = df_test_new['start_time'].sum() / df_test_new['process_start-step1'].sum()
    step1_avgtime_control = df_control_new['step1_time'].sum() / df_control_new['process_step1-step2'].sum()
    step1_avgtime_test = df_test_new['step1_time'].sum() / df_test_new['process_step1-step2'].sum()
    step2_avgtime_control = df_control_new['step2_time'].sum() / df_control_new['process_step2-step3'].sum()
    step2_avgtime_test = df_test_new['step2_time'].sum() / df_test_new['process_step2-step3'].sum()
    step3_avgtime_control = df_control_new['step3_time'].sum() / df_control_new['process_step3-confirm'].sum()
    step3_avgtime_test = df_test_new['step3_time'].sum() / df_test_new['process_step3-confirm'].sum()

    # Creating DataFrame for plotting
    avg_times = pd.DataFrame({
        'Step': ['Start', 'Step1', 'Step2', 'Step3'],
        'Control': [step_avgtime_control, step1_avgtime_control, step2_avgtime_control, step3_avgtime_control],
        'Test': [step_avgtime_test, step1_avgtime_test, step2_avgtime_test, step3_avgtime_test]
    })

    # Calculating overall average time for conclusion
    avg_times['Overall Average'] = avg_times[['Control', 'Test']].mean(axis=1)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor('none')
    text_color = 'white'
    
    for column in ['Control', 'Test', 'Overall Average']:
        ax.plot(avg_times['Step'], avg_times[column], marker='o', label=column)

    ax.set_title('Average Time for Each Step by Group', color=text_color)
    ax.set_xlabel('Step', color=text_color)
    ax.set_ylabel('Average Time in minutes', color=text_color)
    ax.legend()
    ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)

    # Setting tick colors
    ax.tick_params(colors=text_color)

    # Displaying the plot in Streamlit
    st.pyplot(fig, transparent=True)

def drop_rate(data):
    df_control_new = data[data["Variation"] == 'Control']
    df_test_new = data[data["Variation"] == 'Test']

    stepdrop_rate_c = 100 * df_control_new['process_start-dropoff'].sum() / (df_control_new['process_start-dropoff'].sum() + df_control_new['process_start-step1'].sum())
    sdrop_rate_test = 100 * df_test_new['process_start-dropoff'].sum() / (df_test_new['process_start-dropoff'].sum() + df_test_new['process_start-step1'].sum())
    
    step1drop_rate_control = 100 * df_control_new['process_step1-dropoff'].sum() / (df_control_new['process_step1-dropoff'].sum() + df_control_new['process_step1-step2'].sum())
    s1drop_rate_test = 100 * df_test_new['process_step1-dropoff'].sum() / (df_test_new['process_step1-dropoff'].sum() + df_test_new['process_step1-step2'].sum())
    
    step2drop_rate_control = 100 * df_control_new['process_step2-dropoff'].sum() / (df_control_new['process_step2-dropoff'].sum() + df_control_new['process_step2-step3'].sum())
    step2drop_rate_test = 100 * df_test_new['process_step2-dropoff'].sum() / (df_test_new['process_step2-dropoff'].sum() + df_test_new['process_step2-step3'].sum())
    
    step3drop_rate_control = 100 * df_control_new['process_step3-dropoff'].sum() / (df_control_new['process_step3-dropoff'].sum() + df_control_new['process_step3-confirm'].sum())
    step3drop_rate_test = 100 * df_test_new['process_step3-dropoff'].sum() / (df_test_new['process_step3-dropoff'].sum() + df_test_new['process_step3-confirm'].sum())

    # Preparing data for plotting
    steps = ['Start-Step1', 'Step1-Step2', 'Step2-Step3', 'Step3-Confirm']
    control_rates = [stepdrop_rate_c, step1drop_rate_control, step2drop_rate_control, step3drop_rate_control]
    test_rates = [sdrop_rate_test, s1drop_rate_test, step2drop_rate_test, step3drop_rate_test]

    # Plotting
    text_color = 'white'
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(steps, control_rates, marker='o', color='blue', label='Control Drop Rate')
    ax.plot(steps, test_rates, marker='o', color='green', label='Test Drop Rate')

    # Set the plot background to be transparent and color the text to be visible on dark theme
    ax.set_facecolor('none') 
    ax.set_title('Drop Rates by Step for Control and Test Groups (%)', color=text_color)
    ax.set_xlabel('Process Step', color=text_color)
    ax.set_ylabel('Drop Rate (%)', color=text_color)
    ax.set_ylim(0, 100)  # Ensure y-axis goes up to 100%
    
    # Formatting y-axis to show percentages with a "%" sign
    formatter = FuncFormatter(lambda y, _: f'{int(y)}%')
    ax.yaxis.set_major_formatter(formatter)

    # Customize grid to be visible on a dark background
    ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
    
    # Set the tick parameters for both axes to be lighter
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)

    # Set the legend with a lighter text color
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color('black') 

    # Avoiding negative or over 100% labels due to automatic tick selection
    ax.set_yticks(range(0, 101, 10))

    # Displaying the plot in Streamlit
    st.pyplot(fig, transparent=True)

def bounce_rate(data):
    starting_sessions = data[data['process_step'] == 'start']

    # Counting the total number of starting sessions for each group
    total_starting_sessions_control = starting_sessions[starting_sessions['Variation'] == 'Control']['visit_id'].nunique()
    total_starting_sessions_test = starting_sessions[starting_sessions['Variation'] == 'Test']['visit_id'].nunique()

    # Identifying sessions that only have the starting step
    unique_sessions = data.groupby('visit_id').nunique()
    single_step_sessions = unique_sessions[unique_sessions['process_step'] == 1]
    bouncing_sessions = data[data['visit_id'].isin(single_step_sessions.index)]

    # Counting bouncing sessions for each group and calculating bounce rates
    bounce_rate_control = None
    bounce_rate_test = None
    if total_starting_sessions_control > 0:
        bounce_rate_control = 100 * bouncing_sessions[bouncing_sessions['Variation'] == 'Control']['visit_id'].nunique() / total_starting_sessions_control
    if total_starting_sessions_test > 0:
        bounce_rate_test = 100 * bouncing_sessions[bouncing_sessions['Variation'] == 'Test']['visit_id'].nunique() / total_starting_sessions_test

    # Plotting
    text_color = 'white'

    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
    # Setting the face and edge color of the figure to transparent
    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')  # The plot background is transparent
    groups = ['Control', 'Test']
    bounce_rates = [bounce_rate_control if bounce_rate_control is not None else 0,
                    bounce_rate_test if bounce_rate_test is not None else 0]

    # Ensure we have at least one non-None value to plot
    if any(rate is not None for rate in bounce_rates):
        ax.bar(groups, bounce_rates, color=['blue', 'green'])

    ax.set_title('Bounce Rates by Group (%)', color=text_color)
    ax.set_ylabel('Bounce Rate (%)', color=text_color)

    # Set y-axis to show up to 100%
    ax.set_ylim(0, 100)
    
    # Formatting y-axis to show percentages with a "%" sign
    formatter = FuncFormatter(lambda y, _: f'{int(y)}%')
    ax.yaxis.set_major_formatter(formatter)
    
    # Ensure y-axis ticks are set sensibly
    ax.tick_params(axis='both', which='both', length=0)  # Hide the ticks
    ax.tick_params(axis='both', colors=text_color)  # Set the color of the tick labels

    # Customize grid to be visible on a dark background
    ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)

    # Hide the spines
    for spine in ax.spines.values():
        spine.set_visible(False)  # Hide the spines

    # Displaying the plot in Streamlit
    st.pyplot(fig, transparent=True)

def error_rate(data):
    step_mapping = {'start': 0, 'step_1': 1, 'step_2': 2, 'step_3': 3, 'confirm': 4}
    data['step_value'] = data['process_step'].map(step_mapping)
    df_sorted = data.sort_values(by=['visit_id', 'date_time'])
    df_sorted['step_change'] = df_sorted.groupby('visit_id')['step_value'].diff()
    df_sorted['is_error'] = df_sorted['step_change'] < 0
    error_rate_value = df_sorted['is_error'].mean()
    return error_rate_value

