import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to create and display the form in the sidebar
def interview_form():
    st.sidebar.write("### 📝 Candidate Details")

    name = st.sidebar.text_input("👤 Name")
    position = st.sidebar.selectbox("💼 Position", ["Cloud Engineer", "Sr Cloud Engineer", "Cloud Tester", "Sr Cloud Tester", "Architect", "Associate Architect"])
    status = st.sidebar.selectbox("📊 Status", ["Noshow","Cleared", "Rejected"])
    interviewer_name = st.sidebar.selectbox("👥 Interviewer Name", ["...","Surendra Reddy","Naveen", "Rajendra"])
    interview_date = st.sidebar.date_input("📅 Date of Interview")
    interview_round = st.sidebar.number_input("🔢 Round", min_value=1, value=1)

    # Create expander for interview questions and answers
    with st.sidebar.expander("💬 Interview Questions and Answers"):
        num_questions = st.number_input("Enter the number of questions", min_value=1, value=1)
        questions = [st.text_input(f"❓ Question {i+1}") for i in range(num_questions)]
        answers = [st.text_input(f"💬 Answer {i+1}") for i in range(num_questions)]

    submitted = st.sidebar.button("✅ Submit")
    cleared = st.sidebar.button("🗑️ Clear Data")
    
    if submitted:
        # Store the input data in a DataFrame
        new_entry = pd.DataFrame({
            "Name": [name],
            "Position": [position],
            "Status": [status],
            "Interviewer Name": [interviewer_name],
            "Date of Interview": [interview_date],
            "Round": [interview_round],
            "Interview Questions": ["\n".join(questions)],
            "Interview Answers": ["\n".join(answers)]
        })
        st.sidebar.success("👍 Details added successfully!")
        clear_form()
        return new_entry

# Function to clear the form data
def clear_form():
    st.session_state.form_data = {}

# Function to save interview data to a CSV file
def save_data_to_csv(data):
    existing_data = load_data_from_csv()
    updated_data = pd.concat([existing_data, data], ignore_index=True)
    updated_data.to_csv("interview_data.csv", index=False)

# Function to load interview data from a CSV file
def load_data_from_csv():
    try:
        return pd.read_csv("interview_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Position", "Status", "Interviewer Name", "Date of Interview", "Round", "Interview Questions", "Interview Answers"])

# Function to display metrics at the bottom
def display_metrics(interview_data):
    st.write("### 📊 Metrics")

    # Extract unique positions and ensure 'Noshow' status is included in the grouped data
    positions = interview_data['Position'].unique()
    grouped_data = interview_data.groupby(['Position', 'Status']).size().unstack(fill_value=0)
    grouped_data['Noshow'] = 0

    # Extract counts for cleared, rejected, and no-show candidates
    cleared_counts = [grouped_data.loc[position, 'Cleared'] for position in positions]
    rejected_counts = [grouped_data.loc[position, 'Rejected'] for position in positions]
    noshow_counts = [grouped_data.loc[position, 'Noshow'] for position in positions]

    # Define colors for the bars
    colors = {'Cleared': '#4CAF50', 'Rejected': '#FFCDD2', 'No-Show': '#d3d3d3'}

    # Create a stacked bar chart with custom colors
    fig = go.Figure(data=[
        go.Bar(name='Cleared', x=positions, y=cleared_counts, marker_color=colors['Cleared']),
        go.Bar(name='Rejected', x=positions, y=rejected_counts, marker_color=colors['Rejected']),
        go.Bar(name='No-Show', x=positions, y=noshow_counts, marker_color=colors['No-Show'])
    ])

    # Update layout
    fig.update_layout(barmode='stack', xaxis_title='Position', yaxis_title='Count', title='Interview Status by Position')

    # Display the chart
    st.plotly_chart(fig)

# Function to clear interview data
def clear_data():
    if st.button("🗑️ Clear Data", key="clear_button"):
        st.session_state.interview_data = pd.DataFrame(columns=["Name", "Position", "Status", "Interviewer Name", "Date of Interview", "Round", "Interview Questions", "Interview Answers"])
        save_data_to_csv(st.session_state.interview_data)

# Function to download interview data as CSV
def download_data(interview_data):
    if st.button("💾 Download Data"):
        st.download_button(label="Download CSV", data=interview_data.to_csv(index=False), file_name="interview_data.csv", mime="text/csv")

# Main function to run the Streamlit app
def main():
    st.set_page_config(layout="wide")  # Set wide mode
    #st.title(":point_down: :blue[Interview Status Page]")
    st.sidebar.title("📋 Interview Status")
    st.sidebar.image("https://img.freepik.com/free-vector/job-interview-conversation_74855-7566.jpg", use_column_width=True)
    # About section
    st.sidebar.write("---")

    # Load interview data
    interview_data = load_data_from_csv()

    # Create or load the DataFrame
    if 'interview_data' not in st.session_state:
        st.session_state.interview_data = interview_data

    # Display the interview form in the sidebar
    new_entry = interview_form()
    if new_entry is not None:
        # Append the new entry to the DataFrame
        st.session_state.interview_data = pd.concat([st.session_state.interview_data, new_entry], ignore_index=True)
        save_data_to_csv(new_entry)

    tab1, tab2 = st.tabs(["### 👥 Candidate Details", "### 📊 Metrics"])

    with tab1:
        # Display the table of interview data on the main page
        st.write("### 📊 Data")
        st.dataframe(st.session_state.interview_data.style.apply(lambda x: ['background-color: rgba(152, 251, 152, 0.3)' if x.Status == 'Cleared' else 'background-color: rgba(255, 192, 203, 0.3)' if x.Status == 'Rejected' else 'background-color: None' for i in x], axis=1))
        #with st.expander("See explanation"):
            #st.write("Above Table provides the details of the interviews.")

    with tab2:
        # Display metrics at the bottom
        display_metrics(st.session_state.interview_data)

    # Display options in the sidebar
    clear_data()
    download_data(st.session_state.interview_data)

if __name__ == "__main__":
    main()
