import datetime as dt
import io
import logging
import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import clasificacion_core_act
import core_act as activities_loader

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO, # Set the logging level
    handlers=[logging.StreamHandler()] # Ensures output to Streamlit's terminal
)

@st.cache_data
def load_activities():
    return activities_loader.load_activities()

# @st.cache_resource
def load_view_options():
    return {
        "Time view": load_time_view(),
        "Active window view": load_active_window_view(),
        "Activity view": load_activity_view()
    }

def change_color(element_type, widget_label, font_color, background_color='transparent'):
    if element_type == 'select_box':
        query_selector = 'label'
    elif element_type == 'button':
        query_selector = 'button'
    else:
        return

    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('{query_selector}');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
       """
    components.html(f"{htmlstr}", height=1, width=1)


def split_df(input_df, batch_size, current_page):
    start_idx = (current_page - 1) * batch_size
    end_idx = start_idx + batch_size

    return input_df.iloc[start_idx:end_idx]


def paginate_df(dataset):
    def update_input_current_page_before():
        st.session_state.current_page = st.session_state.input_current_page_before
        st.session_state.input_current_page_after = st.session_state.current_page
        st.session_state.input_current_page_before = st.session_state.current_page

    pagination_menu = st.columns((4,1,1))
    with pagination_menu[2]:
        batch_size = st.selectbox("Page Size", options=[10,20,50,100, "all day"], index=2, key="page_size")
        if batch_size=="all day":
            batch_size = len(dataset)

    with pagination_menu[1]:
        total_pages = math.ceil(len(dataset)/ batch_size) 

        if st.session_state.current_page > total_pages:
            st.session_state.current_page = total_pages

        st.session_state.input_current_page_after = st.session_state.current_page
        st.session_state.input_current_page_before = st.session_state.current_page
        st.number_input('Page',min_value = 1, max_value = total_pages,  key='input_current_page_before', on_change=update_input_current_page_before)
        
    with pagination_menu[0]:
        st.markdown(f"Page **{st.session_state.current_page}** of **{total_pages}** ")

    page = split_df(dataset, batch_size, st.session_state.current_page)

    return page, batch_size, total_pages

def apply_styles(page, format_table):

    toggle_block_colours = format_table['toggle_block_colours']
    toggle_begin_end_colours = format_table['toggle_begin_end_colours']
    max_time_between_activities = format_table['max_time_between_activities']


    def resaltar_principio_fin_bloques(fila):
        valor_actual_b = fila['Begin']
        valor_actual_e = fila['End']
        valor_actual_e = pd.to_datetime(valor_actual_e, format='%d/%m/%Y %H:%M')
        fila_sig = st.session_state.df_original.iloc[fila.name + 1] if fila.name + 1 < len(st.session_state.df_original) else None
        fila_ant = st.session_state.df_original.iloc[fila.name - 1] if fila.name - 1 >= 0 else None
        if fila_ant is not None:    
            fila_ant['End'] = pd.to_datetime(fila_ant['End'], format='%d/%m/%Y %H:%M')
        
        dif_tiempo_ant = (valor_actual_b-fila_ant['End']).total_seconds()/60 if fila_ant is not None else 0

        dif_tiempo_sig = (fila_sig['Begin']-valor_actual_e).total_seconds()/60 if fila_sig is not None else 0

        ls_estilos = asignar_color(fila)
        if fila_sig is None or dif_tiempo_sig>max_time_between_activities :

            ls_estilos[6] = 'background-color:#808080' 
        if fila_ant is None or dif_tiempo_ant>max_time_between_activities or fila.name==0 :

            ls_estilos[5] = 'background-color:#808080'
        return ls_estilos  


    if toggle_block_colours and not toggle_begin_end_colours:
        result = page.style.apply(asignar_color,axis=1)
    elif toggle_begin_end_colours:
        result = page.style.apply(resaltar_principio_fin_bloques, axis=1)
    else:
        result = page.style.apply(asignar_color_sin_estilos,axis=1)

    return result
        


def apply_label_to_selection(**kwargs):
    if not "df_original" in st.session_state:
        return
    
    df_original = st.session_state.df_original

    st.session_state.undo_df = df_original.copy()

    for key in kwargs:
        view_options[st.session_state.view_type]['save_func'](key, kwargs[key])


def to_csv(df):
    output = io.BytesIO()
    df.to_csv(output, sep = ";",  index=False, date_format= '%d/%m/%Y %H:%M:%S')
    return output.getvalue().decode('utf-8')

def download_csv(df):
    excel_data = to_csv(df.drop(columns=['Change', 'Begin Time', 'Ending Time', 'ID']))
    st.download_button(
        label="⬇️ Download CSV",
        data=excel_data,
        file_name='dataframe.csv',
        mime='text/csv',
        use_container_width=True
    )

def asignar_color(s):
    col = '#FFFFFF'
    if isinstance(s.Activity, list):
        if len(s.Activity) == 1:
            activity = s.Activity[0]
        else:
            activity = None
    else:
        activity = s.Activity

    if activity in dicc_core_color:
        col = dicc_core_color[activity]
    
    return [f'background-color:{col}']*len(s)
    


def asignar_color_sin_estilos(s):
    return ['background-color:#FFFFFF'] * len(s)

def display_undo_button():
    def undo_last_action():
        st.session_state.df_original = st.session_state.undo_df
        st.session_state.undo_df = None

    st.button("↩️ Undo", disabled=(st.session_state.undo_df is None), on_click = undo_last_action, use_container_width=True)

def display_select_all_button():
    return st.button("✅ Select all in this page", use_container_width=True)

@st.fragment
def display_events_table(df, format_table, batch_size, column_config, column_order=None):        
    select_actions_col = st.columns(3)
    with select_actions_col[0]:
        select_all = st.button("✅ Select all in this page", use_container_width=True)
        if select_all:
            df.loc[:,"Change"] = True
    with select_actions_col[1]:
        select_none = st.button("🚫 Select none in this page", use_container_width=True)
        if select_none:
            df.loc[:,"Change"] = False
    with select_actions_col[2]:
        select_invert = st.button("🔄 Invert selection", use_container_width=True)
        if select_invert:
            df.loc[:,"Change"] = ~(df["ID"].isin(st.session_state.filas_seleccionadas["ID"]))


    styled_df = apply_styles(df, format_table)

    disabled = df.columns.difference(['Change'])

    # Shows table
    edited_df = st.data_editor(
        styled_df,
        column_config=column_config,
        column_order=column_order,
        disabled=disabled,
        hide_index=True,
        key="selector",
        use_container_width = True,
        height= int(35.2*(batch_size+1))
    )


    # Filter rows that have been selected
    filas_seleccionadas = edited_df[edited_df['Change']]
    st.session_state.filas_seleccionadas = filas_seleccionadas

    return filas_seleccionadas

def display_pagination_bottom(total_pages):
    def update_input_current_page_after():
        st.session_state.current_page = st.session_state.input_current_page_after
        st.session_state.input_current_page_before = st.session_state.current_page
        st.session_state.input_current_page_after = st.session_state.current_page

    botton_menu = st.columns((4,1,1))
    with botton_menu[2]:
        st.session_state.input_current_page_after = st.session_state.current_page
        st.number_input('Page',min_value = 1, max_value = total_pages, key='input_current_page_after', on_change=update_input_current_page_after)


def cases_classification():
    def save_case_button(case_name):
        try:
            apply_label_to_selection(Case=case_name)
        except Exception as e:
            logging.exception(f"There was an error saving button {case_name}", exc_info=e)
            st.error("Error saving")

    def add_new_case():
        case_name = st.session_state.new_case_label
        if case_name is not None and case_name != "":
            try:
                apply_label_to_selection(Case=case_name)
                st.session_state.all_cases.add(case_name)
            except Exception as e:
                logging.exception(f"There was an error saving button {case_name}", exc_info=e)
                st.error("Error saving")

    with st.form(key='new_cases', clear_on_submit=True, border=False):
        [col1, col2] = st.columns([0.7, 0.3])
        with col1:
            st.text_input(label="Case label", label_visibility="collapsed", placeholder="Case label", key="new_case_label")
        with col2:
            st.form_submit_button(label="Assign", on_click=add_new_case)

    if len(st.session_state.all_cases) > 1:
        with st.container():
            st.markdown("### Case labels")
            for case in st.session_state.all_cases:
                if case != "":
                    st.button(case, on_click=save_case_button, args=(case,), use_container_width=True)



def manual_classification_sidebar():

    def update_last_3_buttons(core, subact):
        if not "last_acts" in st.session_state:
            return
        
        dicc_aux = {"core_act": core, "subact":subact}
        if dicc_aux not in st.session_state.last_acts:        
            if len(st.session_state.last_acts) > 2:
                st.session_state.last_acts.pop(0) 
            st.session_state.last_acts.append(dicc_aux)


    def save_button(core_act, sub_act):
        try:
            apply_label_to_selection(Activity=core_act, Subactivity=sub_act)
        except Exception as e:
            logging.exception(f"There was an error saving button {core_act}, {sub_act}", exc_info=e)
            st.error("Error saving")


    def save_all_select():
        try: 
            selected = st.session_state.all_select
            split_selection = selected.split(" - ")

            if len(split_selection) == 2:
                seleccion_core_act = split_selection[1]
                seleccion_subact = split_selection[0]

                apply_label_to_selection(Activity=seleccion_core_act, Subactivity=seleccion_subact)
                update_last_3_buttons(seleccion_core_act, seleccion_subact)
                st.session_state.all_select = None

        except Exception as e:
            logging.exception(f"There was an error saving all_select", exc_info=e)
            st.error("Error saving")

    def save_select(core):
        try:
            subact = st.session_state[core]
            apply_label_to_selection(Activity=core, Subactivity=subact)
            update_last_3_buttons(core, subact)
            st.session_state[core] = None
        except Exception as e:
            logging.exception(f"There was an error saving select {core}", exc_info=e)
            st.error("Error saving")    

    if len(st.session_state.last_acts) > 0:
        with st.container():
            st.markdown("###  Last Subactivities")
            ll = [x for x in st.session_state.last_acts if x != ""]            
            subacts = []
            for activity in ll:
                if activity['subact'] is not None and activity['subact'] not in subacts:
                    subacts.append(activity['subact'])
                    st.button(activity['subact'], key=f'boton_{activity["subact"]}', on_click=save_button, args=(activity['core_act'], activity['subact']), use_container_width=True)
                    change_color('button', activity['subact'], 'black', dicc_core_color[activity['core_act']])

    st.selectbox("Search all subactivities", key="all_select", options = all_sub, index=None, placeholder="Search all subactivities", label_visibility='collapsed', on_change=save_all_select)

    for category in dicc_core.keys():
        with st.container():
            st.markdown(f"### {category}")
            for activity in dicc_core[category]:
                core_act = activity['core_activity']
                st.selectbox(core_act, key=core_act, options = dicc_subact[core_act], index=None, placeholder=core_act, label_visibility='collapsed', on_change=save_select, args=(core_act,))
                change_color('select_box', core_act,'black', dicc_core_color[core_act])



def changed_file():
    if "df_original" in st.session_state:
        del st.session_state["df_original"]   

def reset_current_page():
    st.session_state["current_page"] = 1

def automated_classification():
    def run_auto_classify():    
        select_class = st.session_state.auto_type
        openai_key = st.session_state.openai_key
        openai_org = st.session_state.openai_org
        all = st.session_state.df_original 

        if select_class=="Selected date":
            a_datetime = st.session_state.a_datetime
            next_day = st.session_state.next_day
            filter_app = (all['Begin'] >= a_datetime) & (all['Begin'] < next_day)       
            to_classify = all[filter_app]
        
        elif select_class == "Selected rows":
            selected_rows = st.session_state.filas_seleccionadas['ID'].tolist()
            index = [x - 1 for x in selected_rows]
            to_classify = all.iloc[index]
            filter_app = all['ID'].isin(selected_rows)

        else:
            to_classify = all
            filter_app = None

        mensaje_container.write(f"Classifying with GPT {len(to_classify)} elements (it might take a while)...")
        classification = clasificacion_core_act.classify(to_classify, openai_key, openai_org)
        st.session_state.undo_df = all.copy()
        if filter_app is not None:
            all.loc[filter_app,'Activity'] = classification
            all.loc[filter_app,'Subactivity'] = "Unspecified "+classification
        else:
            all['Activity'] = classification
            all['Subactivity'] = "Unspecified "+classification  

      
    with st.expander("Automated labeling"):
        with st.form(key='auto_labeling'):
            st.text_input("Set OpenAI key", type="password", key='openai_key')
            st.text_input("Set OpenAI org", type="password", key='openai_org')

            if view_options[st.session_state.view_type]['has_time_blocks']:
                options = ["All", "Selected date", "Selected rows"]
                index = 1
            else:
                options = ["All"]
                index = 0

            st.selectbox("Choose what data you want to classify", options, index=index, key='auto_type')
        
            st.form_submit_button("Click to start classification", on_click=run_auto_classify) 


def load_time_view():

    def time_view_config(max_dur):
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

    def time_view_options(df):
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
    
    def time_view_save(key, value):
        df_original = st.session_state.df_original
        filas_seleccionadas = st.session_state.filas_seleccionadas['ID'].tolist()
        df_original.loc[df_original['ID'].isin(filas_seleccionadas), key] = value

    
    return {
        "label": "📅 Time view",
        "options_func": time_view_options,
        "config_func": time_view_config,
        "save_func": time_view_save,
        "has_time_blocks": True
    }

def load_active_window_view():

    def active_window_view_config(max_dur):
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

    def active_window_view_options(df):
        filter_column, sort_column = st.columns(2)
        selected_df = df
        with filter_column:
            filter_app = st.selectbox(label='Filter by app:', options=['No filter'] + df['App'].unique().tolist())
            if filter_app != 'No filter':
                selected_df = selected_df[selected_df['App'] == filter_app]

            title_app = st.text_input(label='Filter by window title:')
            if title_app is not None and title_app != '':
                selected_df = selected_df[selected_df['Merged_titles'].str.contains(title_app, case=False)]
                
        with sort_column:
            sort_value = st.selectbox(label='Sort by:', options=['Count', 'Duration'])
            if sort_value == 'Count':
                sort = 'ID'
            else:
                sort = 'Duration'

        selected_df = selected_df.groupby("Merged_titles").agg({"ID": "count", "Duration": "sum", "Activity": lambda x: list(set(x)), "Subactivity":lambda x: list(set(x)), "Case": lambda x: list(set([str(j) for j in x]))}).sort_values(sort, ascending=False).reset_index()
        selected_df["Change"] = False
        selected_df.loc[selected_df["Case"]=='nan', "Case"] = None
        return selected_df

    def active_window_view_save(key, value):
        df_original = st.session_state.df_original
        titles_selected = st.session_state.filas_seleccionadas['Merged_titles'].tolist()
        df_original.loc[df_original['Merged_titles'].isin(titles_selected), key] = value

    
    return {
        "label": "🖥️ Active window view",
        "options_func": active_window_view_options,
        "config_func": active_window_view_config,
        "save_func": active_window_view_save,
        "has_time_blocks": False
    }


def load_activity_view():

    def activity_view_config(max_dur):
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

    def activity_view_options(df):
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

    def activity_view_save(key, value):
        df_original = st.session_state.df_original
        rows = st.session_state.filas_seleccionadas.rename(columns={'Begin': 'Begin_int'})
        result = pd.merge_asof(df_original, rows, left_on='Begin', right_on='Begin_int', by='Subactivity')
        mask = (~(result['Begin_int'].isna())) & (result['Begin'] >= result['Begin_int']) & (result['End_x'] <= result['End_y'])
        df_original.loc[mask, key] = value

    
    return {
        "label": "👩‍💻 Activity view",
        "options_func": activity_view_options,
        "config_func": activity_view_config,
        "save_func": activity_view_save,
        "has_time_blocks": False
    }

@st.fragment
def display_view(selected_view, selected_df, format_table):
    if len(selected_df) == 0:
        st.error("There is no data for the selected filters 😞. Why don't you try with another one? 😉")
    else:
        try:            
            button_column = st.columns(3)
            with button_column[0]:
                display_undo_button()
            with button_column[2]:
                download_csv(st.session_state.df_original)

            page, batch_size, total_pages = paginate_df(selected_df)

            column_config, column_order = selected_view['config_func'](max_dur=selected_df["Duration"].max())

            selected_rows = display_events_table(page, format_table, batch_size, column_config, column_order)
            display_pagination_bottom(total_pages)
        except Exception as e: 
            logging.exception(f"There was an error while displaying the table", exc_info=e)
            st.error("There was an error processing the request. Try again")

def display_label_palette(selected_df):
    if len(selected_df) == 0:
        st.title("Label cases")
        st.warning("No data to label")
        st.title("Label activities")
        st.warning("No data to label")

    else:
        try:
            st.title("Label cases")
            cases_classification()
            st.title("Label activities")
            automated_classification()
            manual_classification_sidebar()
        except Exception as e: 
            logging.exception(f"There was an error while displaying the sidebar", exc_info=e)
            st.error("There was an error processing the request. Try again")

def display_table_formatter(selected_view):
    blocks_column, begin_column = st.columns(2)
    max_time_between_activities = 0
    with blocks_column:
        toggle_block_colours = st.toggle('Blocks colours', value=True)
    with begin_column:
        if selected_view["has_time_blocks"]:
            toggle_begin_end_colours = st.toggle('Begin-End colours')
            if toggle_begin_end_colours:
                max_time_between_activities = st.slider("Maximum time between activities (minutes)", min_value=0, max_value=30, value=5)
        else:
            toggle_begin_end_colours = False

    return {
        'toggle_block_colours': toggle_block_colours,
        'toggle_begin_end_colours': toggle_begin_end_colours,
        'max_time_between_activities': max_time_between_activities
    }



st.set_page_config(layout="wide")

dicc_core, dicc_subact, dicc_map_subact, dicc_core_color = load_activities()
all_sub = [f"{s} - {c}" for c in dicc_subact for s in dicc_subact[c]]

# Upload file
with st.expander("Upload your data"):
    archivo_cargado = st.file_uploader("Upload your Tockler data here. You can export your data by going to Tockler > Search > Set a time period > Export to CSV.", type=["csv"], key="source_file", on_change=changed_file)
    st.write("Alternatively, you can load sample data from https://github.com/project-pivot/labelled-awt-data/")
    load_sample_data = st.button("Load sample data", type="primary", on_click=changed_file)

mensaje_container = st.empty()

if "df_original" not in st.session_state:
    st.session_state["current_page"] = 1
    st.session_state["last_acts"] = []
    st.session_state["next_day"] = None
    st.session_state["a_datetime"] = None
    st.session_state["undo_df"] = None
    st.session_state["all_cases"] = set()

    if archivo_cargado is not None or load_sample_data:
        mensaje_container.write("Loading...")
        if load_sample_data:
            data_expanded = clasificacion_core_act.simple_load_file(url_link="https://raw.githubusercontent.com/project-pivot/labelled-awt-data/main/data/awt_data_1_pseudonymized.csv", dayfirst=True)
        elif archivo_cargado is not None:
            data_expanded = clasificacion_core_act.simple_load_file(loaded_file=archivo_cargado)
        mensaje_container.write("File loaded")

        data_expanded['ID'] = range(1,len(data_expanded)+1)
        data_expanded = data_expanded.reset_index(drop=True)
        data_expanded['Begin'] = pd.to_datetime(data_expanded['Begin'], format='%d/%m/%Y %H:%M:%S')        
        data_expanded['End'] = pd.to_datetime(data_expanded['End'], format='%d/%m/%Y %H:%M:%S')
        data_expanded['Begin Time'] =data_expanded['Begin'].dt.strftime('%H:%M:%S')
        data_expanded['Ending Time']= data_expanded['End'].dt.strftime('%H:%M:%S')
        data_expanded['Change'] = False
        st.session_state.df_original = data_expanded[['Change','ID','Merged_titles','Begin','End','Begin Time','Ending Time', 'Duration', 'Activity', 'Subactivity', 'Case', 'App']]

        st.session_state.all_cases = set(data_expanded["Case"].dropna().unique())
        
if "df_original" in st.session_state:
    view_options = load_view_options()
    
    view_type = st.radio(label="Select view", options=view_options.keys(), format_func=lambda x: view_options[x]['label'], key='view_type', horizontal=True, on_change=reset_current_page)
    selected_view = view_options[view_type]

    selected_df = selected_view['options_func'](st.session_state.df_original)

    format_table = display_table_formatter(selected_view)

    display_view(selected_view, selected_df, format_table)

    with st.sidebar:
        display_label_palette(selected_df)