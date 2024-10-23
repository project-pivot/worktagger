import streamlit as st
import datetime as dt
import pandas as pd
import analysis as wt
from abc import ABC, abstractmethod

class View(ABC):
    @property
    @abstractmethod
    def label(self):
        pass

    @property
    @abstractmethod
    def has_time_blocks(self):
        pass

    @abstractmethod
    def view_config(self, max_dur):
        pass

    @abstractmethod
    def view_filter(self, df, reset_current_page):
        pass

    @abstractmethod
    def view_save(self, key, value):
        pass

class TimeView(View):

    @property
    def label(self):
        return "📅 Time view"
    
    @property
    def has_time_blocks(self):
        return True
    

    def view_config(self, max_dur):
        column_config = {
            "Change": st.column_config.CheckboxColumn(
                "Change",
                help="Choose the rows you want to apply the label",
                default=False,
            ),
            "Begin Time": None,
            "End Time": None,
            "App": None,
            "ID": None,
            '': None,
            "Merged_titles": "App and title",
            "Duration": st.column_config.ProgressColumn(
                label="Duration (seconds)",
                format="%d",
                max_value=max_dur
            )
        }

        column_order = ["Change", "Merged_titles", "Begin", "End", "Duration", "Activity", "Subactivity", "Case"]

        return column_config, column_order

    def view_filter(self, df, reset_current_page):
        date_column, time_column = st.columns(2)
        with date_column:        
            min_date = df['Begin'].dt.date.min()
            max_date=df['Begin'].dt.date.max()
            a_date = st.date_input(f"Pick a date: From {min_date} to {max_date}", min_value=min_date, max_value=max_date, value=(min_date, min_date), on_change=reset_current_page)
        with time_column:
            selected_time = st.time_input("Pick the day start time:", value=dt.time(6, 0))

        filter_activity_col, window_size_col = st.columns(2)
        with filter_activity_col:
            filter_act = st.selectbox(label='Filter by activity:', options=['No filter'] + df['Activity'].unique().tolist())
            filter_case = st.selectbox(label='Filter by case:', options=['No filter'] + df['Case'].unique().tolist())
        with window_size_col:
            window_size = st.slider(label='Select window size:', disabled=((filter_act == 'No filter') and (filter_case == 'No filter')), min_value=0, max_value=15)

        a_combined = [dt.datetime.combine(x, selected_time) for x in a_date]
        a_datetime = a_combined[0]
        if len(a_combined) > 1:
            next_day = a_combined[1] + dt.timedelta(hours=24)
        else:
            next_day = a_combined[0] + dt.timedelta(hours=24)

        st.session_state.a_datetime = a_datetime        
        st.session_state.next_day = next_day

        selected_df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]

        if filter_act != 'No filter' or filter_case != 'No filter':            
            int_act_mask = (selected_df['Activity'] == filter_act).astype(int) if filter_act != 'No filter' else 0
            int_case_mask = (selected_df['Case'] == filter_case).astype(int) if filter_case != 'No filter' else 0
            int_mask = int_act_mask + int_case_mask
            expanded_int_mask = int_mask.rolling(window=2*window_size+1, min_periods=1, center=True).sum()
            expanded_mask = expanded_int_mask > 0
            selected_df = selected_df[expanded_mask]        

        return selected_df
    
    def view_save(self, key, value):
        df_original = st.session_state.df_original
        filas_seleccionadas = st.session_state.filas_seleccionadas['ID'].tolist()
        df_original.loc[df_original['ID'].isin(filas_seleccionadas), key] = value

    

class ActiveWindowView(View):

    @property
    def label(self):
        return "🖥️ Active window view"
    
    @property
    def has_time_blocks(self):
        return False


    def view_config(self, max_dur):
        column_config = {
            "Change": st.column_config.CheckboxColumn(
                "Change",
                help="Choose the rows you want to apply the label",
                default=False,
                disabled=False
            ),
            "ID": "Count",
            "Merged_titles": "App and title",
            "Duration": st.column_config.ProgressColumn(
                label="Duration (seconds)",
                format="%d",
                max_value=max_dur
            ),
            "Activity": "Activities",
            "Subactivity": "Subactivities",
            "Case": "Cases"
        }

        column_order = ["Change", "Merged_titles", "ID", "Duration", "Activity", "Subactivity", "Case"]

        return column_config, column_order

    def view_filter(self, df, reset_current_page):
        filter_column, sort_column = st.columns(2)
        selected_df = df
        with filter_column:
            filter_app = st.selectbox(label='Filter by app:', options=['No filter'] + df['App'].unique().tolist())
            if filter_app != 'No filter':
                selected_df = selected_df[selected_df['App'] == filter_app]

            title_app = st.text_input(label='Filter by window title:')
            if title_app is not None and title_app != '':
                selected_df = selected_df[selected_df['Merged_titles'].str.contains(title_app, case=False)]

            case_filter = st.selectbox(label='Filter by case:', options=['No filter'] + df['Case'].unique().tolist())
                
        with sort_column:
            sort_value = st.selectbox(label='Sort by:', options=['Count', 'Duration'])
            if sort_value == 'Count':
                sort = 'ID'
            else:
                sort = 'Duration'

        selected_df = selected_df.groupby("Merged_titles").agg({"ID": "count", "Duration": "sum", "Activity": lambda x: list(set(x)), "Subactivity":lambda x: list(set(x)), "Case": lambda x: list(set([str(j) if not pd.isna(j) else 'None' for j in x]))}).sort_values(sort, ascending=False).reset_index()
        if case_filter is not None and case_filter != '' and case_filter != 'No filter':
            selected_df = selected_df[selected_df['Case'].apply(lambda x: case_filter in x)]
        selected_df["Change"] = False
        selected_df.loc[selected_df["Case"]=='nan', "Case"] = None
        return selected_df

    def view_save(self, key, value):
        df_original = st.session_state.df_original
        titles_selected = st.session_state.filas_seleccionadas['Merged_titles'].tolist()
        df_original.loc[df_original['Merged_titles'].isin(titles_selected), key] = value

    


class ActivityView(View):

    @property
    def label(self):
        return "👩‍💻 Activity view"
    
    @property
    def has_time_blocks(self):
        return False

    def view_config(self, max_dur):
        column_config = {
            "Change": st.column_config.CheckboxColumn(
                "Change",
                help="Choose the rows you want to apply the label",
                default=False,
                disabled=False
            ),
            "ID": "Windows",
            "Duration": st.column_config.ProgressColumn(
                label="Duration (seconds)",
                format="%d",
                max_value=max_dur
            ), 
            "Case": "Cases"
        }

        column_order = ["Change", "Activity", "Subactivity", "Begin", "End", "ID", "Duration",  "Case"]

        return column_config, column_order

    def view_filter(self, df, reset_current_page):
        filter_column, sort_column = st.columns(2)
        selected_df = df
        with filter_column:
            filter_app = st.selectbox(label='Filter by activity:', options=['No filter'] + df['Activity'].unique().tolist())
            if filter_app != 'No filter':
                selected_df = selected_df[selected_df['Activity'] == filter_app]

            # title_app = st.text_input(label='Filter by title:')
            # if title_app is not None and title_app != '':
            #     selected_df = selected_df[selected_df['Merged_titles'].str.contains(title_app, case=False)]
                
        with sort_column:
            sort_value = st.selectbox(label='Sort by:', options=['Date', 'Count', 'Duration'])
            if sort_value == 'Count':
                sort = 'ID'
                ascending = False
            elif sort_value == 'Duration':
                sort = 'Duration'
                ascending = False
            else:
                sort = 'Begin'
                ascending = True

        changes = ((selected_df['Subactivity'] != selected_df['Subactivity'].shift())) | (selected_df['Begin'].dt.date != selected_df['Begin'].dt.date.shift())
        selected_df = selected_df.groupby(changes.cumsum()).agg({"ID": "count", "Begin": "first", "End": "last", "Duration": "sum", "Activity": lambda x: '||'.join(set(x)), "Subactivity":lambda x: '||'.join(set(x)), "Case": lambda x: list(set([str(j) for j in x])) }).sort_values(sort, ascending=ascending).reset_index(drop=True)
        selected_df["Change"] = False
        selected_df.loc[selected_df["Case"]=='nan', "Case"] = None
        return selected_df

    def view_save(self, key, value):
        df_original = st.session_state.df_original
        rows = st.session_state.filas_seleccionadas.rename(columns={'Begin': 'Begin_int'})
        result = pd.merge_asof(df_original, rows, left_on='Begin', right_on='Begin_int', by='Subactivity')
        mask = (~(result['Begin_int'].isna())) & (result['Begin'] >= result['Begin_int']) & (result['End_x'] <= result['End_y'])
        df_original.loc[mask, key] = value

    


class WorkSlotView(View):

    @property
    def label(self):
        return "⌚️ Work slot view"
    
    @property
    def has_time_blocks(self):
        return False


    def view_config(self, max_dur):
        column_config = {
            "Change": st.column_config.CheckboxColumn(
                "Change",
                help="Choose the rows you want to apply the label",
                default=False,
            ),
            "Begin Time": None,
            "End Time": None,
            "App": None,
            "ID": None,
            '': None,
            "Merged_titles": "App and title",
            "Duration": st.column_config.ProgressColumn(
                label="Duration (seconds)",
                format="%d",
                max_value=max_dur
            )
        }

        column_order = ["Change", "Merged_titles", "Begin", "End", "Duration", "Activity", "Subactivity", "Case"]

        return column_config, column_order

    def view_filter(self, df, reset_current_page):
        selected_df = df
        slots_config, filter_config = st.columns(2)
        with filter_config:
            case_filter = st.selectbox(label='Filter by case:', options=['No filter'] + df['Case'].unique().tolist())

        with slots_config:
            interval = st.slider("Select inactivity threshold (seconds):", min_value=0, max_value=300, value=60, on_change=reset_current_page)
            slots = wt.find_temporal_slots(selected_df, inactivity_threshold=pd.Timedelta(f'{interval}s'))
            if case_filter is not None and case_filter != '' and case_filter != 'No filter':
                case_in_filter = (selected_df['Case'] == case_filter)
                real_filter = case_in_filter.groupby(slots).transform('any')
                selected_df = selected_df[real_filter]
                slots = wt.find_temporal_slots(selected_df, inactivity_threshold=pd.Timedelta(f'{interval}s'))

        with filter_config:
            unique = selected_df.groupby(slots)['Case'].transform('nunique')
            num_case_types_filter = st.slider(label='Filter by a number of case types in work slot greater or equal than:', min_value=0, max_value=unique.max())
            if num_case_types_filter > 0:
                selected_df = selected_df[unique >= num_case_types_filter]
                slots = wt.find_temporal_slots(selected_df, inactivity_threshold=pd.Timedelta(f'{interval}s'))

        with slots_config:
            min_slot = slots.min() + 1
            max_slot = slots.max() + 1
            slot_number = st.number_input(f'Select slot number ({min_slot} - {max_slot}):',min_value = min_slot, max_value =max_slot)



        selected_df = selected_df[slots==(slot_number-1)]

        return selected_df
    
    def view_save(self, key, value):
        df_original = st.session_state.df_original
        filas_seleccionadas = st.session_state.filas_seleccionadas['ID'].tolist()
        df_original.loc[df_original['ID'].isin(filas_seleccionadas), key] = value

    
