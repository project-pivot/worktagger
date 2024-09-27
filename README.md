<div align="center">
  
# Work Tagger
### A Labelling Companion

<img src="https://github.com/user-attachments/assets/f6f9b4f5-dd50-4baa-8a80-dd6165702efe" alt="work_tagger" width="400" style="border: 1px solid #ddd; padding: 4px;"/>

[![Visit Work Tagger](https://img.shields.io/badge/Visit-Work%20Tagger-blue?style=flat)](https://worktagger.streamlit.app/)
</div>


Work Tagger is a web-based tool that facilitates the classification of AWT data. Work Tagger has been developed using Streamlit, which is an open-source Python framework to create interactive web-applications, whose main characteristic is that it integrates the development of both a web-based frontend and backend into a single Python code base.

Work Tagger is designed to use the AWT data collected by an application called Tockler, which records all active windows on the computer while the application is installed and running. We have chosen Tockler because it is open source and runs locally, which helps to avoid privacy concerns. However, Work Tagger is designed to easily integrate data coming from other similar tools.

The web-based user interface of Work Tagger allows users to upload files, select data for classification, and visualize the results using different views. The user interface is designed to be user-friendly and interactive, featuring dynamic UI elements such as buttons, select boxes and sliders for ease of use. Streamlit's interactive widgets enhance user experience by providing responsive and intuitive controls.

Once users upload their AWT logs (in csv format) through the user interface, the backend processes these files, converting them into a dataframe. During this process, columns are prepared with the necessary formats for efficient data manipulation.

In contrast to other web-based tools, Work Tagger does not use a database for data storage. Instead, Work Tagger relies on session state variables to store data temporarily. This approach ensures that each user's data is isolated and managed independently, preventing conflicts in a multi-user environment. These session state variables are maintained for the duration of the user's interaction with the application, ensuring a personalized and consistent experience. Additionally, this decision is related to privacy concerns, we do not store records of individuals' computer usage, thus protecting users' personal information and ensuring their privacy.

When the AWT log is loaded in the application, Work Tagger displays the AWT events in a table and allows the user to label the events with the activity and case the user was performing at that moment. For activities, the user may opt to undertake the classification process either manually or automatically. In the former case, the user has to choose the activity from a predefined list of activities and subactivities. However, Work Tagger is designed so that the set of activities can be easily modified. In the latter case, once automatic classification is initiated, the backend logic sends the data to the classification core to interact with the OpenAI API to perform zero-shot classification using the GPT-4o model based on the same set of activities and subactivities used in the manual classification. We opted for this approach to provide a highly flexible and adaptive classification system that does not require training the model beforehand.

Concerning the labeling of cases, only manual labeling is possible. Moreover, unlike activities, the set of cases are open and users can pick from case labels already used in the dataset or can enter new case labels. The reason for following a different approach for cases is because, unlike activities, they are very specific to a particular person and a particular moment in time. 

## Running Work Tagger Locally

To run Work Tagger locally, follow these steps:

1. Clone the repository to your local machine.
2. Open a terminal and navigate to the root directory of the repository.
3. Install the dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Run the following command to launch the application:
   ```bash
   python -m streamlit run app_core_act.py
   ```

## Adding Core Activities as a Developer

To add new core activities and their respective subactivities to Work Tagger, follow these steps:

1. Open the `core_act.py`file located in the repository.
2. Inside this file, locate the `load_activities`function, which contains a dictionary called `dicc_core`.
3. This dictionary stores the predefined core activities. It has sseveral keys such as `"General"`, `"General (extended)"`, `"Education"`, and `"Research"`, with each key mapping to a list of dictionaries. Each dictionary represents a core activity with the following structure:
   - `core_activity`: The name of the core activity.
   - `color`: The color associated with this activity (used for UI representation).
   - `activities`: A list of subactivities related to this core activity.
  
To add a new core activity, follow these steps:

1. Choose the appropriate key (e.g., `"General"`.`"Education"`, etc.) based on the category of your new core activity.
2. Add a new dictionary to the corresponding list. This dictionary should follow the structure of existing entries, as shown below:
   ```python
   {
      "core_activity": "Your new core activity name",
      "color": "#YourColorCode",  # Specify a color for UI representation
      "activities": [
         "First subactivity description",
         "Second subactivity description",
         "Third subactivity description"
      ]
   }
   ```

## Demo Video

For a detailed demonstration, you can watch the [Work Tagger demo on YouTube](https://www.youtube.com/watch?v=ulVh63TyR6k).


## References

Beerepoot, Iris, Barenholz, Daniël, Beekhuis, Stijn, Gulden, Jens, Lee, Suhwan, Lu, Xixi, Overbeek, Sietse, Van De Weerd, Inge, Van Der Werf, Jan Martijn, and Reijers, Hajo A. "A Window of Opportunity: Active Window Tracking for Mining Work Practices." In *2023 5th International Conference on Process Mining (ICPM)*, pp. 57-64. IEEE, 2023.
