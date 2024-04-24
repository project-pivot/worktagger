# %%
import pandas as pd
import numpy as np

#!pip install cohere tiktoken
#!pip install scikit-llm==0.4.2
#!pip install scikit-learn

# %%
from skllm import MultiLabelZeroShotGPTClassifier
from skllm import ZeroShotGPTClassifier
from skllm.config import SKLLMConfig
from skllm.datasets import get_multilabel_classification_dataset
from skllm.preprocessing import GPTSummarizer

# %%
configuracion_openai = 'openai_config.csv'
df_openai = pd.read_csv(configuracion_openai, sep=",")
clave = df_openai['Key'].iloc[0]
organizacion = df_openai['Organization'].iloc[0]

# %%
SKLLMConfig.set_openai_key(clave)
SKLLMConfig.set_openai_org(organizacion)

# %%
df = pd.read_csv("archivo_temporal.csv",sep=";")
df.head(5)
#df.to_csv('ruta_del_resultado.csv', sep=';')

# %%
"""Display the time period of the data."""

#print(df['Begin'].min(), 'until', df['End'].max())

# %%
"""Concatenate the app and title."""

df['Title'] = df['App'] +" - "+ df["Title"]
df.head(5)

# %%
"""Adds a new column that specifies whether the type of recording is work or computer break."""

df['Type'] = "Computer work"

# Set 'Type' to 'NATIVE - NO_TITLE' where 'Title' is 'NATIVE - NO_TITLE'
df['Type'] = np.where(df['Title'].str.contains('NO_TITLE'), 'NO_TITLE', df['Type'])


# %%
df

# %%
"""We add new rows when there is a gap in the time between two rows, and add the rows to the data, with the category "Computer break"."""

new_rows = []
for i in range(len(df) - 1):
  current_end_time = df.loc[i, 'End']
  next_start_time = df.loc[i + 1, 'Begin']
  if current_end_time != next_start_time:
    new_row = {'App': "n.a.", 'Type': "n.a.", 'Title': "Computer break", 'Begin': current_end_time, 'End': next_start_time, 'Type': "Computer break"}
    new_rows.append(new_row)

df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

# %%
"""Add a column for the duration between the start and end time and calculate the total duration of recorded data."""

df['Begin'] = pd.to_datetime(df['Begin'], errors='coerce')
df['End'] = pd.to_datetime(df['End'], errors='coerce')
df["Duration"] = df['End'] - df['Begin']

#print(df['Duration'].sum())


# %%
"""Merge all titles between computer breaks."""

df_merged_titles = df

# Sort the DataFrame by 'Begin' to ensure the data is in chronological order
df_merged_titles = df.sort_values(by='Begin')

# Add a new column 'Previous_App' to represent the app in the previous row
df_merged_titles['Previous_App'] = df_merged_titles['App'].shift(1)

# Create a new column 'Merged_title' and initialize it with 'Title' column values
df_merged_titles['Merged_titles'] = df_merged_titles['Title']

# Group by 'Type' and create a new column 'Group' to identify consecutive rows with the same 'Type'
df_merged_titles['Group'] = (df_merged_titles['Type'] != df_merged_titles['Type'].shift(1)).cumsum()

# %%
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

# %%
# Group by 'Type' and 'Group', and apply the custom aggregation function
result_df = df_merged_titles.groupby(['Type', 'Group']).apply(custom_aggregation).reset_index(drop=True)

# Drop the temporary 'Group' column if it exists
if 'Group' in result_df.columns:
    result_df.drop(columns=['Group'], inplace=True)

# Sort the resulting DataFrame by the 'Begin' column
result_df.sort_values(by='Begin', inplace=True)

# Reset the index after sorting
result_df.reset_index(drop=True, inplace=True)

result_df

# %%
"""Add a column with the most occurring title."""

# Define a custom function to find the most occurring title in a semicolon-separated string
def find_most_occurring_title(merged_titles):
    titles = merged_titles.split(';')
    title_counts = pd.Series(titles).value_counts()
    most_occuring_title = title_counts.idxmax()
    return most_occuring_title

# Apply the custom function to each row in the DataFrame and create a new column
result_df['Most_occuring_title'] = result_df['Merged_titles'].apply(find_most_occurring_title)

# Display the updated DataFrame
result_df

# %%
"""Filter the dataframe to only contain rows where type is computer work, because I only want to classify those rows."""

filtered_df = result_df[result_df['Type'] == 'Computer work'].copy()[:150]



# %%
"""Apply Zero-Shot Text Classification."""

# Assuming result_df is a DataFrame with a column "Merged_titles"
X = filtered_df["Merged_titles"].tolist()

# Zero-shot classification
candidate_labels = [
    "Actively contributing to social debates",
    "Assessing the students? assignments and submitting the assessment to the Board of Examiners",
    "Adapting a publication",
    "Assessing exams and giving marks",
    "Communicating about events",
    "Communicating to students about the teaching material and assessment",
    "Conducting research",
    "Discussing possible assignments with students",
    "Discussing the structure, provision and progress of the assignment with students",
    "Drafting a research plan",
    "Drafting conference papers",
    "Drafting exam papers",
    "Drafting publications for recognised academic journals and trade journals",
    "Encouraging and giving lectures",
    "Exploring the societal need for research",
    "Following specific courses",
    "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)",
    "Organizing national and international travelling",
    "Organizing practical aspects for the group",
    "Organizing practical aspects of events",
    "Participating in group meetings",
    "Periodically discussing research results with fellow researchers and supervisor or co-supervisor",
    "Planning teaching activities",
    "Preparing and providing teaching sessions for students, providing prospective students with information",
    "Proposing events",
    "Requesting and assessing leave",
    "Reviewing",
    "Supervising and discussing the progress of the partial or completed research with PhD candidates"
]
candidate_labels_2 = [
    "?g?r ?t?rk",
    "Active Window Tracking",
    "AI Lab for Public Services",
    "Benjamin Kleppe",
    "BISE special issue on mismatches event data and reality",
    "BPM 2023",
    "BPM conference 2023",
    "BPM course",
    "BPM paper combination SWORD and motivation model",
    "BPM paper combination SWORD and motivational model",
    "BPM&A group",
    "BPMA Group",
    "Brainstorm 15-3-2023",
    "Brainstorm seminar on PM human-in-the-loop",
    "Dagmar van den Berg",
    "Dagstuhl seminar on Human in the Process Mines",
    "ECIS 2023",
    "ECIS 2023 workarounds workshop",
    "ECIS paper on RPA priorities  ",
    "EWUU seed fund predictive process monitoring",
    "Future of Work Lunch meeting ",
    "Future of Work Think paper",
    "Girls Club WIN",
    "Guest lecture NWI bachelor",
    "Human resource perspective in Process Mining",
    "ICIS 2023 routines track",
    "ICS department",
    "Ivonne Mangula",
    "Karst van de Vendel",
    "Map metaphor",
    "March holiday",
    "Max Gompel",
    "MethodsX paper Identifying Grand Challenges",
    "OTP Workload Monitor",
    "RCIS 2023",
    "RCIS paper on recording techniques",
    "RCIS paper recording techniques",
    "Sam Kooijman",
    "SOFTX-D-23-00057",
    "Stijn Beekhuis",
    "Tim van Holst",
    "Tutorial on task support for PM",
    "Ying Liu"
]



# %%
# Create a prompt template by concatenating original text with contextual information
prompt_template = (
    "I am an assistant professor at a university in The Netherlands and I have been recording my computer behavior. "
    "I had a tool record the computer windows that I had active at a certain time. "
    "I want you to try to work out what task I was working on during that time.\n\n"
    "You will be provided with the following information:\n"
    "1. One or more window titles. The titles include the app and the title of the screen. They are ordered in the order that they occurred.\n"
    "2. A list of task categories that you may choose from.\n\n"
    "Perform the following tasks:\n"
    "1. Identify to which category the provided window titles belong with the highest probability.\n"
    "2. Assign the provided text to that category.\n\n"
    "Window titles:\n{}\n\nCandidate labels:\n{}"
)

# Format the prompt for each instance in the dataset
formatted_prompts = [
    prompt_template.format("\n".join(f"- {title}" for title in text.split(";")), "\n".join(candidate_labels))
    for text in X
]


# %%
# Set the maximum number of tokens you want to keep
max_tokens = 4000

# Truncate each text in the formatted_prompts list to the specified number of tokens
truncated_prompts = [prompt[:max_tokens] for prompt in formatted_prompts]

# Create and fit the MultiLabelZeroShotGPTClassifier
clf = ZeroShotGPTClassifier(openai_model="gpt-4-1106-preview")
clf.fit(truncated_prompts, [candidate_labels])

# Predict labels for the truncated prompts
labels = clf.predict(truncated_prompts)

# Add the predicted labels to a new column
filtered_df["Zero_shot_classification"] = labels

# %%
import random

# Print 10 random truncated prompts and their predicted labels
random_indices = random.sample(range(len(truncated_prompts)), 10)

for index in random_indices:
    prompt = truncated_prompts[index]
    predicted_label = labels[index]

    #print(f"Prompt: {prompt}\n")
    #print(f"Predicted Label: {predicted_label}\n")

# %%
# Path to the text file in Google Colab (adjust the path as needed)
output_file_path = 'example_classifications.txt'

# Open the file in write mode
with open(output_file_path, 'w', encoding="utf-8") as output_file:
    # Print 10 random truncated prompts and their predicted labels
    random_indices = random.sample(range(len(truncated_prompts)), 10)

    for index in random_indices:
        prompt = truncated_prompts[index]
        predicted_label = labels[index]

        # Write the information to the file
        output_file.write(f"Prompt: {prompt}\n\n")
        output_file.write(f"Predicted Label: {predicted_label}\n\n")

# Print the file path
#print(f"Results written to: {output_file_path}")

# Text summarization
#s = GPTSummarizer(openai_model="gpt-4", max_words=15)
#summaries = s.fit_transform(X)

# Add the summaries to a new column
#result_df["Zero_shot_summary"] = summaries

"""Write results to file."""

try:
    filtered_df.to_excel('resultados.xlsx', index=False)
    #filtered_df.to_csv('ruta_del_resultado.csv', sep=';')
    #print("Results written to: resultados.xlsx")
except Exception as e:
    print(f"Error writing results to file: {e}")

# %%
#filtered_df

# %%
#!pip install openpyxl


# %%
# Guardar el DataFrame como un archivo Excel en el sistema de archivos local de Colab
#filtered_df.to_excel('/content/result.xlsx', index=False)

# Mostrar mensaje de confirmación
#print("Archivo 'result.xlsx' guardado en el sistema de archivos local de Colab.")



# %%
#from google.colab import files

#files.download('result.xlsx')


# %%
#from google.colab import files

# Descargar el archivo CSV
#files.download('/content/result.csv')


# %%
#!ls /content/

# %%
#import shutil
#import tempfile
#from google.colab import files

# Directorio temporal
#temp_dir = tempfile.mkdtemp()

# Ruta completa al archivo result.csv
#file_path = '/content/result.csv'

# Copiar el archivo al directorio temporal
#shutil.copy(file_path, temp_dir)

# Mostrar la ruta del archivo copiado
#temp_file_path = f"{temp_dir}/result.csv"
#print(f"Archivo copiado a: {temp_file_path}")

# Descargar manualmente desde el directorio temporal
# Puedes hacer clic derecho en el archivo en el panel de archivos de Colab y seleccionar "Descargar"


# %%



