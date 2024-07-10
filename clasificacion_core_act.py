import pandas as pd
import numpy as np

from skllm import MultiLabelZeroShotGPTClassifier
from skllm import ZeroShotGPTClassifier
from skllm.config import SKLLMConfig
from skllm.datasets import get_multilabel_classification_dataset
from skllm.preprocessing import GPTSummarizer
import streamlit as st
import io
import warnings

warnings.filterwarnings("ignore")

# clave = st.session_state.openai_key
# organizacion = st.session_state.openai_org

# SKLLMConfig.set_openai_key(clave)
# SKLLMConfig.set_openai_org(organizacion)


def simple_load_file(loaded_file):
    ficheros_subidos = io.BytesIO(loaded_file.read())
    ficheros_subidos.seek(0)

    df = pd.read_csv(ficheros_subidos,sep=";")
    if "Zero_shot_classification" in df.columns:
        return df
    else:
        df['Merged_titles'] = df['App'] +" - "+ df["Title"]
        #Adds a new column that specifies whether the type of recording is work or computer break.
        df['Type'] = "Computer work"
        # Set 'Type' to 'NATIVE - NO_TITLE' where 'Title' is 'NATIVE - NO_TITLE'
        df['Type'] = np.where(df['Title'].str.contains('NO_TITLE'), 'NO_TITLE', df['Type'])
        df['Begin'] = pd.to_datetime(df['Begin'], format='%d/%m/%Y %H:%M', errors='coerce')
        df['End'] = pd.to_datetime(df['End'], format='%d/%m/%Y %H:%M', errors='coerce')
        df["Duration"] = df['End'] - df['Begin']
        return df[df['Type'] == 'Computer work'].copy()




def load_uploaded_file(loaded_file):
    ficheros_subidos = io.BytesIO(loaded_file.read())
    ficheros_subidos.seek(0)

    df = pd.read_csv(ficheros_subidos,sep=";")
    #Concatenate the app and title.
    df['Title'] = df['App'] +" - "+ df["Title"]
    #Adds a new column that specifies whether the type of recording is work or computer break.
    df['Type'] = "Computer work"
    # Set 'Type' to 'NATIVE - NO_TITLE' where 'Title' is 'NATIVE - NO_TITLE'
    df['Type'] = np.where(df['Title'].str.contains('NO_TITLE'), 'NO_TITLE', df['Type'])

    #We add new rows when there is a gap in the time between two rows, and add the rows to the data, with the category "Computer break".
    new_rows = []
    for i in range(len(df) - 1):
        current_end_time = df.loc[i, 'End']
        next_start_time = df.loc[i + 1, 'Begin']
        if current_end_time != next_start_time:
            new_row = {'App': "n.a.", 'Type': "n.a.", 'Title': "Computer break", 'Begin': current_end_time, 'End': next_start_time, 'Type': "Computer break"}
            new_rows.append(new_row)

    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    #Add a column for the duration between the start and end time and calculate the total duration of recorded data.

    df['Begin'] = pd.to_datetime(df['Begin'], errors='coerce')
    df['End'] = pd.to_datetime(df['End'], errors='coerce')
    df["Duration"] = df['End'] - df['Begin']

    #Merge all titles between computer breaks.
    df_merged_titles = df

    # Sort the DataFrame by 'Begin' to ensure the data is in chronological order
    df_merged_titles = df.sort_values(by='Begin')

    # Add a new column 'Previous_App' to represent the app in the previous row
    df_merged_titles['Previous_App'] = df_merged_titles['App'].shift(1)

    # Create a new column 'Merged_title' and initialize it with 'Title' column values
    df_merged_titles['Merged_titles'] = df_merged_titles['Title']

    # Group by 'Type' and create a new column 'Group' to identify consecutive rows with the same 'Type'
    df_merged_titles['Group'] = (df_merged_titles['Type'] != df_merged_titles['Type'].shift(1)).cumsum()

    # Define a custom aggregation function for the 'agg' method
    def custom_aggregation(group):
        return pd.Series({
            'Merged_titles': ';'.join(map(str, group['Merged_titles'])),
            'Begin': group['Begin'].iloc[0],
            'End': group['End'].iloc[-1],
            'App': group['App'].iloc[0],
            'Type': group['Type'].iloc[0],
            'Duration': group['Duration'].sum()  # Assuming you want to sum the durations
            # Add more columns as needed
        })
    
    # Group by 'Type' and 'Group', and apply the custom aggregation function
    result_df = df_merged_titles.groupby(['Type', 'Group']).apply(custom_aggregation).reset_index(drop=True)

    # Drop the temporary 'Group' column if it exists
    if 'Group' in result_df.columns:
        result_df.drop(columns=['Group'], inplace=True)

    # Sort the resulting DataFrame by the 'Begin' column
    result_df.sort_values(by='Begin', inplace=True)

    # Reset the index after sorting
    result_df.reset_index(drop=True, inplace=True)

    #Add a column with the most occurring title.

    # Define a custom function to find the most occurring title in a semicolon-separated string
    def find_most_occurring_title(merged_titles):
        titles = merged_titles.split(';')
        title_counts = pd.Series(titles).value_counts()
        most_occuring_title = title_counts.idxmax()
        return most_occuring_title

    # Apply the custom function to each row in the DataFrame and create a new column
    result_df['Most_occuring_title'] = result_df['Merged_titles'].apply(find_most_occurring_title)

    #Filter the dataframe to only contain rows where type is computer work, because I only want to classify those rows.

    filtered_df = result_df[result_df['Type'] == 'Computer work'].copy()

    return filtered_df


def gpt_classification(filtered_df, openai_key=None, openai_org=None):
    
    #Apply Zero-Shot Text Classification.

    # Assuming result_df is a DataFrame with a column "Merged_titles"
    X = filtered_df["Merged_titles"].tolist()

    core_activities = {
        "Faculty plan/capacity group plan": "Provide input and collect and document ideas and priorities from the chair",
        "Management of education and research": "Managing and supervising the education and research corresponding to the chair",
        "Human Resources policy": "Execution of the HR policies established by the dean within the chair",
        "Organizational matters": "Following organizational policies regarding HR matters, finances, IT and security",
        "Programme development" : "Ensuring the development of academic teaching programmes tailored to the needs of students and society",
        "Acquisition of contract teaching and research" : "Acquiring and developing contract teaching and research",
        "Accountability for contract teaching and research" :  "Assessing and correcting the realisation of contract research and teaching",
        "Advancing/communicating scientific knowledge and insight": "Representing as well as encouraging the advancement of knowledge and insight in their own field of expertise in respect of the scientific community, society and the public and private sectors if possible.",
        "Working groups and committees": "Participating in and/or managing committees or working groups, both internally and externally, as well as carrying out assigned management and administrative duties as the representative of the chair",
        "Contribution to the research group or lab": "Contributing to the group in various ways, e.g. through exchanging ideas, lessons learned, mentoring more junior colleagues, etc.",
        "Organization of (series of) events": "Organizing events or series of external events, including scientific events such as conferences and workshops, but also outreach. ",
        "Provision of education": "Ensuring the provision and quality of course components",
        "Student supervision" : "Ensuring the supervision and support of students as well as assessing students in the execution and progress of assignments",
        "PhD candidates" : "Appointing, supervising and assessing PhD candidates as a Supervisor in the execution and progress of doctoral research",
        "Education development" : "Analysing the level of the students and the needs of society",
        "Testing" :  "Testing learning outcomes using the assessment methods developed and/or approved by the teaching institute",
        "Education evaluation" : "Contributing to the evaluation of the format and the provision of course components as well as submitting proposals regarding potential improvements in the teaching and/or content of these course components",
        "Education coordination" : "Coordinating (the development of) a programme and the provision of assigned course components",
        "Research development" : "Initiating and developing scientific research programmes based on developments in their own field and in line with societal needs and opportunities for valorisation of the knowledge to be developed",
        "Assessment of research" : "Contributing to the assessment of research in the community",
        "Execution of research" : "Ensuring the execution and quality of research",
        "Publication of research" : "Publishing research results",
        "Research coordination" : "Coordinating and monitoring the cohesion within a research programme and monitoring the progress of their own research",
        "Research proposal" : "Becoming familiar with and defining the subject and theoretical framework",
        "Research plan" : "Formulating a research question and working hypotheses as well as determining research methods and target groups",
        "Performing research" : "Collecting, analysing and interpreting research data, both empirically and theoretically",
        "Doctoral thesis" : "Writing a doctoral thesis in consultation with the supervisor"

    }


    prompt_template = (
        "I am an assistant professor at a university in The Netherlands and I have been recording my computer behavior. "
        "I had a tool record the computer windows that I had active at a certain time. "
        "I want you to try to work out what task I was working on during that time.\n\n"
        "You will be provided with the following information:\n"
        "1. One or more window titles. The titles include the app and the title of the screen. They are ordered in the order that they occurred.\n"
        "2. A list of task categories that you may choose from.\n\n"
        "3. The description of each task category.\n\n"
        "Perform the following tasks:\n"
        "1. Identify to which category the provided window titles belong with the highest probability.\n"
        "2. Assign the provided text to that category.\n\n"
        "Window titles:\n{}\n\nCandidate labels:\n{}"
        "Output ONLY the name of the category NOT the description"
    )

    candidate_labels_2 = [f"{key}: {value}" for key, value in core_activities.items()]
    candidate_labels = [key for key,value in core_activities.items()]

    # Format the prompt for each instance in the dataset
    formatted_prompts = [
        prompt_template.format("\n".join(f"- {title}" for title in text.split(";")), "\n".join(candidate_labels_2))
        for text in X
    ]

    # Set the maximum number of tokens you want to keep
    max_tokens = 4000

    # Truncate each text in the formatted_prompts list to the specified number of tokens
    truncated_prompts = [prompt[:max_tokens] for prompt in formatted_prompts]

    # Create and fit the MultiLabelZeroShotGPTClassifier
    clf = ZeroShotGPTClassifier(openai_model="gpt-4-1106-preview", openai_key=openai_key, openai_org=openai_org)
    clf.fit(truncated_prompts, [candidate_labels])

    # Predict labels for the truncated prompts
    labels = clf.predict(truncated_prompts)

    # Add the predicted labels to a new column
    filtered_df["Zero_shot_classification"] = labels

    return filtered_df

