import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import datetime as dt
import clasificacion_core_act
import core_act as activities_loader
import io
import math
import warnings

warnings.filterwarnings("ignore")


@st.cache_data
def load_activities():
    return activities_loader.load_activities()

def create_selectbox(core_act):    
    selectbox = st.selectbox(core_act, key=core_act, options = [''] + dicc_subact[core_act], on_change=save_select, args=(core_act,))
    change_select_box_color(core_act,'black', dicc_core_color[core_act])

    return selectbox

def create_buttons(option):
    boton = st.button(option['subact'], key=f'boton_{option["subact"]}', on_click=save_button, args=(option['core_act'], option['subact']))
    change_button_color(option['subact'], 'black', dicc_core_color[option['core_act']])

    return boton

def change_select_box_color(widget_label, font_color, background_color='transparent'):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('label');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
       """
    components.html(f"{htmlstr}", height=1, width=1)



def change_button_color(widget_label, font_color, background_color='transparent'):
    
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
       """
    components.html(f"{htmlstr}", height=1, width=1)

def split_df(input_df, batch_size):
    df = [input_df.loc[i:i+batch_size-1,:] for i in range(input_df.index.min(),input_df.index.min()+len(input_df), batch_size)]
    return df

# To update the shared value from input_number1
def update_input_current_page_before():
    st.session_state.current_page = st.session_state.input_current_page_before
    st.session_state.input_current_page_after = st.session_state.current_page
    st.session_state.input_current_page_before = st.session_state.current_page

# To update the shared value from input_number2
def update_input_current_page_after():
    st.session_state.current_page = st.session_state.input_current_page_after
    st.session_state.input_current_page_before = st.session_state.current_page
    st.session_state.input_current_page_after = st.session_state.current_page

def paginate_df(dataset):
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

    pages = split_df(dataset,batch_size)

    page = pages[st.session_state.current_page-1]

    return page, batch_size, total_pages

def apply_styles(page, toggle_block_colours, toggle_begin_end_colours):
    if toggle_block_colours and not toggle_begin_end_colours:
        result = page.style.apply(asignar_color,axis=1)
    elif toggle_begin_end_colours:
        result = page.style.apply(resaltar_principio_fin_bloques, axis=1)
    else:
        result = page.style.apply(asignar_color_sin_estilos,axis=1)

    return result
        
def going_back():
    st.session_state.df_original = st.session_state.undo_df
    st.session_state.undo_df = None
    #st.write("st.df y st.last se supone que son iguales")



def save_button(core_act, sub_act):
    try:
        apply_label_to_selection(core_act, sub_act)
    except Exception as e:
        print(f"There was an error saving button {core_act}, {sub_act}: {e}")
        st.error("Error saving")


def save_all_select():
    try: 
        selected = st.session_state.all_select
        split_selection = selected.split(" - ")

        if len(split_selection) == 2:
            seleccion_core_act = split_selection[1]
            seleccion_subact = split_selection[0]

            apply_label_to_selection(seleccion_core_act, seleccion_subact)
            update_last_3_buttons(seleccion_core_act, seleccion_subact)
            st.session_state.all_select = ""

    except Exception as e:
        print(f"There was an error saving all_select: {e}")
        st.error("Error saving")

def save_select(core):
    try:
        subact = st.session_state[core]
        apply_label_to_selection(core, subact)
        update_last_3_buttons(core, subact)
        st.session_state[core] = ""
    except Exception as e:
        print(f"There was an error saving select {core}: {e}")
        st.error("Error saving")
    
def apply_label_to_selection(core, subact):
    if not "df_original" in st.session_state:
        return
    
    df_original = st.session_state.df_original
    filas_seleccionadas = st.session_state.filas_seleccionadas

    st.session_state.undo_df = df_original.copy()

    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Subactivity'] = subact
    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Activity'] = core

def update_last_3_buttons(core, subact):
    if not "last_acts" in st.session_state:
        return
    
    dicc_aux = {"core_act": core, "subact":subact}
    if dicc_aux not in st.session_state.last_acts:        
        if len(st.session_state.last_acts) > 0:
            st.session_state.last_acts.pop(0) 
        st.session_state.last_acts.append(dicc_aux)

def to_csv(df):
    output = io.BytesIO()
    df.to_csv(output, sep = ";",  index=False, date_format= '%d/%m/%Y %H:%M')
    return output.getvalue().decode('utf-8')

def download_csv(df):
    excel_data = to_csv(df.drop(columns=['Change', 'Begin Time', 'Ending Time', 'ID']))
    st.download_button(
        label="Download CSV",
        data=excel_data,
        file_name='dataframe.csv',
        mime='text/csv'
    )

def asignar_color(s):
    col = dicc_core_color[s.Activity]
    return ['background-color:{}'.format(col)]*len(s)
    
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


def asignar_color_sin_estilos(s):
    return ['background-color:#FFFFFF'] * len(s)

def display_events_table(df, batch_size, total_pages, max_dur):
    st.button("Undo", disabled=(st.session_state.undo_df is None), on_click = going_back)
        
    column_config = {
        "Change": st.column_config.CheckboxColumn(
            "Change",
            help="Choose the rows you want to apply the label",
            default=False,
        ),
        # "Begin": st.column_config.DatetimeColumn(
        #     label="Begining",
        #     format="D MMM YYYY, h:mm a",
        #     min_value=dt.datetime(2023, 6, 1),
        #     max_value=dt.datetime(2025, 1, 1)
        # ),        
        "Begin": None,
        "End": None,
        "ID": None,
        '': None,
        "Merged_titles": "App and title",
        "Duration": st.column_config.ProgressColumn(
            label="Duration (seconds)",
            format="%d",
            max_value=max_dur
        )

    }

    # Shows table
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        disabled=["ID", 'Merged_titles', 'Begin', 'End','Begin Time','Ending Time', 'App', 'Type', 'Duration', 'Most_occuring_title', 'Activity','Subactivity'],
        hide_index=True,
        key="selector",
        use_container_width = True,
        height= int(35.2*(batch_size+1))
    )
    botton_menu = st.columns((4,1,1))
    with botton_menu[2]:
        st.session_state.input_current_page_after = st.session_state.current_page
        st.number_input('Page',min_value = 1, max_value = total_pages, key='input_current_page_after', on_change=update_input_current_page_after)

    # Filter rows that have been selected
    filas_seleccionadas = edited_df[edited_df['Change']]['ID'].tolist()
    st.session_state.filas_seleccionadas = filas_seleccionadas

    st.markdown('</div>', unsafe_allow_html=True)
    return filas_seleccionadas


def manual_classification_sidebar():
    st.selectbox("Search all subactivities", key="all_select", options = [''] + all_sub, on_change=save_all_select)

    contenedores={}
    contenedores["Last subactivities"] = st.container()
    boton = None
    with contenedores["Last subactivities"]:
        st.markdown("###  Last Subactivities")
        ll = [x for x in st.session_state.last_acts if x != ""]            
        subacts = []
        for activity in ll:
            if not activity['subact'] in subacts:
                boton = create_buttons(activity)
                subacts.append(activity['subact'])

    for category in dicc_core.keys():
        contenedores[category] = st.container()
        with contenedores[category]:
            st.markdown(f"### {category}")
            for activity in dicc_core[category]:
                selectbox = create_selectbox(activity['core_activity'])
    
    st.markdown(
        """<style>           

        .element-container button {
            color: black;
            width: 100%; /* Ancho fijo para todos los botones */
            text-align: center;
            display: inline-block;
            
            border-radius: 4px;
        }

        </style>""",
        unsafe_allow_html=True,
    )
    if selectbox:
        st.success(f'Updated label successfully.')
        #edited_df['Change'] = False
        st.empty()
    if boton:
        st.success(f'Updated label successfully.')
        #edited_df['Change'] = False
        st.empty()




def changed_file():
    # Delete all the items in Session state
    #if st.session_state["source_file"]:
    if "df_original" in st.session_state:
        del st.session_state["df_original"]   

def reset_current_page():
    st.session_state["current_page"] = 1

def automated_classification():
    with st.expander("Automated labeling"):
        with st.form(key='auto_labeling'):
            st.text_input("Set OpenAI key", type="password", key='openai_key')
            st.text_input("Set OpenAI org", type="password", key='openai_org')
            st.selectbox("Choose what data you want to classify", ["All", "Selected date", "Selected rows"], index=1, key='auto_type')
        
            st.form_submit_button("Click to start classification", on_click=run_auto_classify) 

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
        selected_rows = st.session_state.filas_seleccionadas
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


st.set_page_config(layout="wide")

dicc_core, dicc_subact, dicc_core_color = load_activities()
all_sub = [f"{s} - {c}" for c in dicc_subact for s in dicc_subact[c]]

# Upload file
with st.expander("Upload your data"):
    archivo_cargado = st.file_uploader("Upload your Tockler data here. You can export your data by going to Tockler > Search > Set a time period > Export to CSV.", type=["csv"], key="source_file", on_change=changed_file)

mensaje_container = st.empty()

if "df_original" not in st.session_state:
    st.session_state["current_page"] = 1
    st.session_state["last_acts"] = []
    st.session_state["next_day"] = None
    st.session_state["a_datetime"] = None
    st.session_state["undo_df"] = None

    if archivo_cargado is not None:
        mensaje_container.write("Loading...")
        data_expanded = clasificacion_core_act.simple_load_file(archivo_cargado)
        mensaje_container.write("File loaded")

        data_expanded['ID'] = range(1,len(data_expanded)+1)
        data_expanded = data_expanded.reset_index(drop=True)
        data_expanded['Begin'] = pd.to_datetime(data_expanded['Begin'], format='%d/%m/%Y %H:%M')        
        data_expanded['End'] = pd.to_datetime(data_expanded['End'], format='%d/%m/%Y %H:%M')
        data_expanded['Begin Time'] =data_expanded['Begin'].dt.strftime('%H:%M:%S')
        data_expanded['Ending Time']= data_expanded['End'].dt.strftime('%H:%M:%S')
        data_expanded['Change'] = False
        st.session_state.df_original = data_expanded[['Change','ID','Merged_titles','Begin','End','Begin Time','Ending Time', 'Duration', 'Activity', 'Subactivity']]
        
if "df_original" in st.session_state:
    select_date_col, select_colors_col = st.columns(2)
    with select_colors_col:     
        toggle_block_colours = st.toggle('Blocks colours', value=True)
        toggle_begin_end_colours = st.toggle('Begin-End colours')
        max_time_between_activities = st.slider("Maximum time between activities (minutes)", min_value=0, max_value=30, value=5)
    
    with select_date_col:
        df = st.session_state.df_original
        min_date = df['Begin'].dt.date.min()
        max_date=df['Begin'].dt.date.max()
        st.write(f"Date range: From {min_date} to {max_date}")
        
        a_date = st.date_input("Pick a date", min_value=min_date, max_value=max_date, value=min_date, on_change=reset_current_page)
        selected_time = st.time_input("Pick a time", value=dt.time(6, 0))

        a_datetime = dt.datetime.combine(a_date, selected_time)
        st.session_state.a_datetime = a_datetime

        next_day = a_datetime + dt.timedelta(hours=24)
        st.session_state.next_day = next_day


    selected_df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
    
    if len(selected_df) == 0:
        st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")
    else:
        try:
            page, batch_size, total_pages = paginate_df(selected_df)
            styled_page = apply_styles(page, toggle_block_colours, toggle_begin_end_colours)
            selected_rows = display_events_table(styled_page, batch_size, total_pages, max_dur=selected_df["Duration"].max())

            with st.sidebar:
                st.title("Classify activities")
                automated_classification()
                manual_classification_sidebar()

            download_csv(st.session_state.df_original)
        except Exception as e: 
            print(f"There was an error: {e}")
            st.error("There was an error processing the request. Try again")