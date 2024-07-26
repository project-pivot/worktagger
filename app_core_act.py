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
    selectbox = st.selectbox(core_act, key=core_act, options = [''] + dicc_subact[core_act], on_change=lambda: save_select(core_act))
    change_select_box_color(core_act,'black', dicc_core_color[core_act])

    return selectbox

def creacion_botones(option):
    boton = st.button(option['subact'], key=f'boton_{option["subact"]}', on_click=lambda: save_button(option['core_act'], option['subact']))
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

def paginate_df(dataset, tipo):
    botton_menu = st.columns((4,1,1))
    with botton_menu[2]:
        batch_size = st.selectbox("Page Size", options=[10,20,50,100, "all day"], index=0, key="page_size")
        if batch_size=="all day":
            batch_size = len(dataset)

    with botton_menu[1]:
        total_pages = math.ceil(len(dataset)/ batch_size) 

        if st.session_state.current_page > total_pages:
            st.session_state.current_page = total_pages
            st.session_state.input_current_page_before = st.session_state.current_page
            st.session_state.input_current_page_after = st.session_state.current_page

        st.number_input('Page',min_value = 0, max_value = total_pages,  value=st.session_state.current_page, key='input_current_page_before', on_change=update_input_current_page_before)
        
    with botton_menu[0]:
        st.markdown(f"Page **{st.session_state.current_page}** of **{total_pages}** ")

    pages = split_df(dataset,batch_size)


    if tipo=="Sin estilos":
        st.session_state.df = pages[st.session_state.current_page-1].style.apply(asignar_color_sin_estilos,axis=1)
    
    elif tipo=="Estilos":
        st.session_state.df = pages[st.session_state.current_page-1].style.apply(asignar_color,axis=1)
    
    else: 
        st.session_state.df = pages[st.session_state.current_page-1].style.apply(resaltar_principio_fin_bloques, axis=1)

    return batch_size, total_pages
        
def going_back():
    st.session_state.df = st.session_state.last_df
    st.write("st.df y st.last se supone que son iguales")

def reset_selects():
    for core_act in dicc_subact.keys():
        st.session_state[core_act] = ""

    st.session_state["all_select"] = ""

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
            reset_selects()

    except Exception as e:
        print(f"There was an error saving all_select: {e}")
        st.error("Error saving")

def save_select(core):
    try:
        subact = st.session_state[core]
        apply_label_to_selection(core, subact)
        update_last_3_buttons(core, subact)
        reset_selects()
    except Exception as e:
        print(f"There was an error saving select {core}: {e}")
        st.error("Error saving")
    
def apply_label_to_selection(core, subact):
    df_original = st.session_state.df_original
    st.session_state.last_df = st.session_state.df
    filas_seleccionadas = st.session_state.filas_seleccionadas

    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Subactivity'] = subact
    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Zero_shot_classification'] = core

def update_last_3_buttons(core, subact):
    dicc_aux = {"core_act": core, "subact":subact}
    if dicc_aux not in st.session_state.last_acts:
        st.session_state.last_acts.pop(0)
        st.session_state.last_acts.append(dicc_aux)

def to_csv(df):
    output = io.BytesIO()
    df.to_csv(output, sep = ";",  index=False, date_format= '%d/%m/%Y %H:%M')
    return output.getvalue().decode('utf-8')

def download_csv(df):
    excel_data = to_csv(df.drop(columns=['Change']))
    st.download_button(
        label="Download CSV",
        data=excel_data,
        file_name='dataframe.csv',
        mime='text/csv'
    )

def asignar_color(s):
    col = dicc_core_color[s.Zero_shot_classification]
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
    if fila_sig is None or dif_tiempo_sig>tiempo_maximo_entre_actividades :

        ls_estilos[6] = 'background-color:#808080' 
    if fila_ant is None or dif_tiempo_ant>tiempo_maximo_entre_actividades or fila.name==0 :

        ls_estilos[5] = 'background-color:#808080'
    return ls_estilos  


def asignar_color_sin_estilos(s):
    return ['background-color:#FFFFFF'] * len(s)

def clasificar_manualmente(df, batch_size, total_pages):
    go_back = st.button("Back", disabled=True, on_click = going_back)
    if go_back:
        df = st.session_state.last_df
        st.session_state.original = st.session_state.last_df
        st.session_state.df = st.session_state.last_df
        
    column_config = {
        "Change": st.column_config.CheckboxColumn(
            "Change",
            help="Choose the rows you want to apply the label",
            default=False,
        ),
        "Begin": None,
        "End": None,
        "ID": None,
        '': None
    }

    # Mostrar la interfaz de edición
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        disabled=["ID", 'Merged_titles', 'Begin', 'End','Begin Time','Ending Time', 'App', 'Type', 'Duration', 'Most_occuring_title', 'Zero_shot_classification','Subactivity'],
        hide_index=True,
        key="selector",
        use_container_width = True,
        height= int(35.2*(batch_size+1))
    )
    botton_menu = st.columns((4,1,1))
    with botton_menu[2]:
        st.number_input('Page',min_value = 1, max_value = total_pages, value=st.session_state.current_page, key='input_current_page_after', on_change=update_input_current_page_after)

    # Filtrar las filas que han sido seleccionadas para cambiar la clasificación
    filas_seleccionadas = edited_df[edited_df['Change']]['ID'].tolist()
    st.session_state.filas_seleccionadas = filas_seleccionadas

    # Mostrar una selección para cambiar la clasificación manualmente
    with st.sidebar:
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
                    boton = creacion_botones(activity)
                    subacts.append(activity['subact'])

        for category in dicc_core.keys():
            contenedores[category] = st.container()
            with contenedores[category]:
                st.markdown("### {}".format(category))
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
            st.success(f'Selected row sort order updated successfully.')
            edited_df['Change'] = False
            st.empty()
        if boton:
            st.success(f'Selected row sort order updated successfully.')
            edited_df['Change'] = False
            st.empty()

    st.markdown('</div>', unsafe_allow_html=True)


def changed_file():
    # Delete all the items in Session state
    if st.session_state["source_file"]:
        del st.session_state["notebook_ejecutado"]    
        del st.session_state["esperando_resultados"]    
        if "df" in st.session_state:
            del st.session_state["df"]
        if "df_original" in st.session_state:
            del st.session_state["df_original"]   

def reset_current_page():
    st.session_state["current_page"] = 1


st.set_page_config(layout="wide")

dicc_core, dicc_subact, dicc_core_color = load_activities()
all_sub = [f"{s} - {c}" for c in dicc_subact for s in dicc_subact[c]]

# Upload file
with st.expander("Click for upload"):
    openai_key = st.text_input("Set OpenAI key", type="password")
    openai_org = st.text_input("Set OpenAI org", type="password")
    archivo_cargado = st.file_uploader("Upload a file", type=["csv"], key="source_file", on_change=changed_file)

if "notebook_ejecutado" not in st.session_state:
    st.session_state["notebook_ejecutado"] = False

if "esperando_resultados" not in st.session_state:
    st.session_state["esperando_resultados"] = True

if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1
    st.session_state["input_current_page_before"] = 1
    st.session_state["input_current_page_after"] = 1
if "last_acts" not in st.session_state:
    st.session_state["last_acts"] = ["","",""]
if "last_df" not in st.session_state:
    st.session_state["last_df"] = None


mensaje_container = st.empty()
if archivo_cargado is not None and not st.session_state.notebook_ejecutado:
    mensaje_container.write("Loading...")

    if openai_key and openai_org:
        filtered_df = clasificacion_core_act.load_uploaded_file(archivo_cargado)
        mensaje_container.write(f"Classifying with GPT {len(filtered_df)} elements (it might take a while)...")
        filtered_df = clasificacion_core_act.gpt_classification(filtered_df, openai_key, openai_org)#, mensaje_container)
        st.session_state.notebook_ejecutado = True
    else:
        filtered_df = clasificacion_core_act.simple_load_file(archivo_cargado)
        if "Zero_shot_classification" not in filtered_df.columns:
            filtered_df['Zero_shot_classification'] = "No work-related"
        mensaje_container.write("File loaded")

    st.session_state.esperando_resultados = False


# Verificar si se encontró el archivo de resultados
if not st.session_state.esperando_resultados:
    # El archivo de resultados ha sido encontrado, mostrar mensaje de éxito

    if "df" not in st.session_state:
        data = filtered_df
        data_expanded = data.assign(Merged_titles=data['Merged_titles'].str.split(';')).explode('Merged_titles')
        data_expanded['ID'] = range(1,len(data_expanded)+1)
        data_expanded = data_expanded.reset_index(drop=True)
        data_expanded['Begin'] = pd.to_datetime(data_expanded['Begin'], format='%d/%m/%Y %H:%M')
        
        data_expanded['End'] = pd.to_datetime(data_expanded['End'], format='%d/%m/%Y %H:%M')
        data_expanded['Begin Time'] =data_expanded['Begin'].dt.strftime('%H:%M')
        data_expanded['Ending Time']= data_expanded['End'].dt.strftime('%H:%M')
        st.session_state.df = data_expanded
        st.session_state.df['Change'] = False
        st.session_state.df = data_expanded[['Change','ID','Merged_titles','Begin','End','Begin Time','Ending Time', 'Zero_shot_classification']]
        ls =  st.session_state.df['Zero_shot_classification'].map(dicc_subact)
        ls_subact = []
        for el in ls:
            ls_subact.append(el[0])

        
        st.session_state.df['Subactivity'] = ls_subact#["📊 Data Exploration"]*len(st.session_state.df)
        
        st.session_state.df_original = st.session_state.df

    col00, col01 = st.columns(2)
    with col01:     
        toggle_block_colours = st.toggle('Blocks colours')
        toggle_begin_end_colours = st.toggle('Begin-End colours')
        tiempo_maximo_entre_actividades = st.slider("Maximum time between activities (minutes)", min_value=0, max_value=30, value=5)
        if toggle_block_colours and not toggle_begin_end_colours:
            pagination_style = "Estilos"
        elif toggle_begin_end_colours:
            pagination_style = "Resalto"
        else:
            pagination_style = "Sin estilos"
    
    with col00:
        df = st.session_state.df_original
        df['Begin'] = pd.to_datetime(df['Begin'], format='%d/%m/%Y %H:%M', errors = 'coerce')  # Asegurarse de que la columna 'Begin' sea de tipo datetime
        min_date = df['Begin'].dt.date.min()
        max_date=df['Begin'].dt.date.max()

        st.write(f"Date range: From {min_date} to {max_date}")
        
        a_date = st.date_input("Pick a date", min_value=min_date, max_value=max_date, value=min_date, on_change=reset_current_page)
        selected_time = st.time_input("Pick a time", value=dt.time(6, 0))
        # Obtener la fecha y hora seleccionadas
        a_datetime = dt.datetime.combine(a_date, selected_time)
        # Calcular la fecha y hora exactas de 24 horas posteriores
        next_day = a_datetime + dt.timedelta(hours=24)


    st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
    if len(st.session_state.df) == 0:
        st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")
    else:
        try:
            batch_size, total_pages = paginate_df(st.session_state.df, pagination_style)
            clasificar_manualmente(st.session_state.df, batch_size, total_pages)
            download_csv(df)
        except Exception as e: 
            print(f"There was an error: {e}")
            st.error("There was an error processing the request. Try again")