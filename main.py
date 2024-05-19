from pygwalker.api.streamlit import StreamlitRenderer
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


from streamlit_vizzu import VizzuChart, Data, Config, Style

# Function to create and display the form in the sidebar
def interview_form():
    st.sidebar.write("### 📝 Candidate Details")

    name = st.sidebar.text_input("👤 Name")
    position = st.sidebar.selectbox("💼 Position", ["Cloud Engineer", "Sr Cloud Engineer", "Cloud Tester", "Sr Cloud Tester", "Architect", "Associate Architect"])
    status = st.sidebar.selectbox("📊 Status", ["Noshow","Cleared", "Rejected"])
    interviewer_name = st.sidebar.selectbox("👥 Interviewer Name", ["...","Surendra Reddy","Naveen", "Rajendra", "Chetan", "Pranav"])
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
    st.session_state.interview_data = pd.DataFrame(columns=["Name", "Position", "Status", "Interviewer Name", "Date of Interview", "Round", "Interview Questions", "Interview Answers"])
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
    st.write("### 📊 Results")

    # Extract unique positions
    positions = interview_data['Position'].unique()

    # Initialize dictionaries to store counts for each metric
    first_round_counts = {position: {'Cleared': 0, 'Rejected': 0, 'No-Show': 0} for position in positions}
    second_round_counts = {position: {'Cleared': 0, 'Rejected': 0, 'No-Show': 0} for position in positions}

    # Loop through the interview data to count candidates for each round and status
    for _, row in interview_data.iterrows():
        position = row['Position']
        status = row['Status']
        round_number = row['Round']
        if round_number == 1:
            first_round_counts[position][status] += 1
        elif round_number == 2:
            second_round_counts[position][status] += 1

    # Define colors for the bars
    colors = {'Cleared': '#4CAF50', 'Rejected': '#FFCDD2', 'No-Show': '#d3d3d3'}

    # Create separate bar charts for each round
    fig1 = go.Figure()
    fig2 = go.Figure()

    for status, color in colors.items():
        fig1.add_trace(go.Bar(name=status, x=positions, y=[first_round_counts[position][status] for position in positions], marker_color=color))
        fig2.add_trace(go.Bar(name=status, x=positions, y=[second_round_counts[position][status] for position in positions], marker_color=color))

    # Update layout
    fig1.update_layout(barmode='group', xaxis_title='Position', yaxis_title='Count', title='Round 1 - Interview Status by Position')
    fig2.update_layout(barmode='group', xaxis_title='Position', yaxis_title='Count', title='Round 2 - Interview Status by Position')

    # Display the charts
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)



# # Function to clear interview data
# """ def clear_data():
#     if st.button("🗑️ Clear Data", key="clear_button"):
#         st.session_state.interview_data = pd.DataFrame(columns=["Name", "Position", "Status", "Interviewer Name", "Date of Interview", "Round", "Interview Questions", "Interview Answers"])
#         save_data_to_csv(st.session_state.interview_data) """

# Function to download interview data as CSV
def download_data(interview_data):
    if st.button("💾 Download Data"):
        st.download_button(label="Download CSV", data=interview_data.to_csv(index=False), file_name="interview_data.csv", mime="text/csv")

# graph heatmap
def graph_heatmap():
    d_types = {
    "Name": str,
    "Position": str,
    "Status": str,
    "Interviewer Name": str,
    "Date of Interview": str,
    "Round": str,
    "Interview Questions": str,
    "Interview Answers": str,
    }
    df = pd.read_csv("interview_data.csv", dtype=d_types)
    data = Data()
    data.add_df(df)

    chart = VizzuChart()
    chart.feature("tooltip", True)
    chart.animate(data)

    chart.animate(
        Data.filter(
            "(record['Position'] == 'Cloud Engineer'||record['Position'] == 'Associate Architect') && (record['Status'] == 'Cleared'||record['Status'] == 'Rejected')"
        ),
        Config(
            {
                "coordSystem": "cartesian",
                "geometry": "rectangle",
                "x": "Round",
                "y": {"set": "Status", "range": {"min": "auto", "max": "auto"}},
                "color": "count()",
                "lightness": None,
                "size": None,
                "noop": None,
                "split": False,
                "align": "none",
                "orientation": "horizontal",
                "label": "Status",
                "sort": "byValue",
            }
        ),
        Style(
            {
                "plot": {
                    "yAxis": {"label": {"numberScale": "shortScaleSymbolUS"}},
                    "xAxis": {"label": {"numberScale": "shortScaleSymbolUS"}},
                    "marker": {
                        "label": {
                            "numberFormat": "prefixed",
                            "maxFractionDigits": "1",
                            "numberScale": "shortScaleSymbolUS",
                        },
                        "rectangleSpacing": 0,
                        "circleMinRadius": 0.005,
                        "borderOpacity": 1,
                        "colorPalette": "#4171cd",
                    },
                }
            }
        ),
    )

    chart.show()

# Stacked Chart
def graph_stacked_chart():
    d1_types = {
    "Name": str,
    "Position": str,
    "Status": str,
    "Interviewer Name": str,
    "Date of Interview": str,
    "Round": str,
    "Interview Questions": str,
    "Interview Answers": str,
    }
    df1 = pd.read_csv("interview_data.csv", dtype=d1_types)
    data1 = Data()
    data1.add_df(df1)

    chart1 = VizzuChart(key="stacked_chart")
    chart1.feature("tooltip", True)
    chart1.animate(data1)

    chart1.animate(
        Data.filter(
            "(record['Position'] == 'Cloud Engineer'||record['Position'] == 'Associate Architect') && (record['Status'] == 'Cleared'||record['Status'] == 'Rejected')"
        ),
        Config(
            {
                "coordSystem": "cartesian",
                "geometry": "rectangle",
                "x": "Round",
                "y": {
                    "set": ["Status", "count()"],
                    "range": {"min": "auto", "max": "auto"},
                },
                "color": "Status",
                "lightness": None,
                "size": None,
                "noop": None,
                "split": False,
                "align": "stretch",
                "orientation": "horizontal",
                "label": "Status",
                "sort": "byValue",
            }
        ),
        Style(
            {
                "plot": {
                    "yAxis": {"label": {"numberScale": "shortScaleSymbolUS"}},
                    "xAxis": {"label": {"numberScale": "shortScaleSymbolUS"}},
                    "marker": {
                        "label": {
                            "numberFormat": "prefixed",
                            "maxFractionDigits": "1",
                            "numberScale": "shortScaleSymbolUS",
                        },
                        "rectangleSpacing": None,
                        "circleMinRadius": 0.005,
                        "borderOpacity": 1,
                        "colorPalette": "#03ae71 #f4941b #f4c204 #d49664 #f25456 #9e67ab #bca604 #846e1c #fc763c #b462ac #f492fc #bc4a94 #9c7ef4 #9c52b4 #6ca2fc #5c6ebc #7c868c #ac968c #4c7450 #ac7a4c #7cae54 #4c7450 #9c1a6c #ac3e94 #b41204",
                    },
                }
            }
        ),
    )

    chart1.show()

# Main function to run the Streamlit app
def main():
    st.set_page_config(layout="wide")  # Set wide mode
    hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
    st.markdown(hide_footer_style, unsafe_allow_html=True)
    #st.title(":point_down: :blue[Interview Status Page]")
    st.sidebar.title("📋 Interview Status")
    st.sidebar.image("https://img.freepik.com/free-vector/job-interview-conversation_74855-7566.jpg", use_column_width=True)
    # About section
    st.sidebar.write("---")

    st.header("👥 Interview Details Application ", divider="violet")
    

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

    #tab1, tab2, tab3 = st.tabs(["### 👥 Candidate Details", "### 📊 Metrics", "### 📈 Graphs"])
    tab1, tab2, tab3 = st.tabs(["### 👥 Candidate Details", "### 📊 Results","### 📈 More Visualization"])

    with tab1:
        # Display the table of interview data on the main page
        st.write("### 📊 Data")
        st.dataframe(st.session_state.interview_data.style.apply(lambda x: ['background-color: rgba(152, 251, 152, 0.3)' if x.Status == 'Cleared' else 'background-color: rgba(255, 192, 203, 0.3)' if x.Status == 'Rejected' else 'background-color: None' for i in x], axis=1))
        #with st.expander("See explanation"):
            #st.write("Above Table provides the details of the interviews.")
        download_data(st.session_state.interview_data)


    with tab2:
        # Display metrics at the bottom
        display_metrics(st.session_state.interview_data)
       

    # You should cache your pygwalker renderer, if you don't want your memory to explode


    with tab3:
        @st.cache_resource
        def get_pyg_renderer() -> "StreamlitRenderer":
            df = pd.read_csv("./interview_data.csv")
            # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
            return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")


        renderer = get_pyg_renderer()

        renderer.explorer()
        
    #     with col1:
    #         graph_heatmap()

    #     with col2:
    #         graph_stacked_chart()

    # Display options in the sidebar
    #clear_data()   

    

if __name__ == "__main__":
    main()
