import streamlit as st
import pandas as pd
import nbformat
from nbconvert import PythonExporter
import sys
import time
import os
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
import datetime as dt
import clasificacion_core_act
import core_act
import io
from io import BytesIO
import warnings

warnings.filterwarnings("ignore")


@st.cache_data
def load_activities():
    return core_act.load_activities()

def creacion_selectbox(option):
    
    selectbox = st.selectbox(option, key=option, options = [''] + dicc_subact[option], on_change=guardar)
    ChangeSelectBoxColour(option,'black', dicc_core_color[option])

    return selectbox

def creacion_botones(col0, col1, counter,option):
    if counter%2 == 0:
        with col0:
            boton = st.button(option, key=option, on_click=guardar)
            ChangeButtonColour(option, 'black', dicc_core_color[option])


    else:
        with col1:
            boton = st.button(option, key=option, on_click=guardar)
            ChangeButtonColour(option, 'black', dicc_core_color[option])

    return boton

def ChangeSelectBoxColour(widget_label, font_color, background_color='transparent'):
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



def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
    
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

def split_df(input_df,filas):
    
    df = [input_df.loc[i:i+filas-1,:] for i in range(input_df.index.min(),input_df.index.min()+len(input_df), filas)]
    
    return df

def paginate_df(name, dataset, tipo):
    botton_menu = st.columns((4,1,1))
    with botton_menu[2]:
        #batch_size = st.selectbox("Page Size", options=[10,20,50,100], key=f"{name}")
        st.session_state.batch_size = st.selectbox("Page Size", options=[10,20,50,100, "all day"], key=f"{name}")
        if st.session_state.batch_size=="all day":
            st.session_state.batch_size = int(len(dataset))
    with botton_menu[1]:
        total_pages = (
            int(len(dataset)/ st.session_state.batch_size) if int(len(dataset) / st.session_state.batch_size) >0 else 1
            
        )
        current_page = st.number_input(
            "Page", min_value=1, max_value=total_pages, step=1)
        
    with botton_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    pages = split_df(dataset,st.session_state.batch_size)

    if tipo=="Sin estilos":
        st.session_state.df = pages[current_page-1].style.apply(asignar_color_sin_estilos,axis=1)
    
    elif tipo=="Estilos":
        st.session_state.df = pages[current_page-1].style.apply(asignar_color,axis=1)
    
    else: 
        st.session_state.df = pages[current_page-1].style.apply(resaltar_principio_fin_bloques, axis=1)

def reset():
    for core_act in dicc_subact.keys():
        st.session_state[core_act] = ""

    st.session_state["all_select"] = ""
    


def guardar():
    df_original = st.session_state.df_original
    seleccion_core_act = [clave for clave, valor in st.session_state.items() if isinstance(valor, str) and valor != "" and valor !="all day" and clave!="openai_key" and clave!="openai_org"]
    seleccion_subact = [valor for clave, valor in st.session_state.items() if isinstance(valor, str) and valor != "" and valor!="all day" and clave!="openai_key" and clave!="openai_org"]
    filas_seleccionadas = st.session_state.filas_seleccionadas

    if seleccion_core_act[0] == "all_select":
        split_selection = seleccion_subact[0].split(" - ")

        if len(split_selection) == 2:
            seleccion_core_act = [split_selection[1]]
            seleccion_subact = [split_selection[0]]
        else:
            seleccion_core_act = []
            seleccion_subact = []

    if len(seleccion_core_act) > 0 and len(seleccion_subact) > 0:
        df_original.loc[df['ID'].isin(filas_seleccionadas), 'Subactivity'] = seleccion_subact*len(filas_seleccionadas)
        df_original.loc[df['ID'].isin(filas_seleccionadas), 'Zero_shot_classification'] = seleccion_core_act*len(filas_seleccionadas)
   
    reset()
    

def to_csv(df):
    output = io.BytesIO()
    df.to_csv(output, sep = ";",  index=False, date_format= '%d/%m/%Y %H:%M')
    return output.getvalue().decode('utf-8')

def finalizar_cambios():
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

def clasificar_manualmente(df):
    
    column_config = {
        "Change": st.column_config.CheckboxColumn(
            "Change",
            help="Elige las filas a las que haya que cambiar su clasificación",
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
        height= int(35.2*(st.session_state.batch_size+1))
    )
    
    # Filtrar las filas que han sido seleccionadas para cambiar la clasificación
    filas_seleccionadas = edited_df[edited_df['Change']]['ID'].tolist()
    st.session_state.filas_seleccionadas = filas_seleccionadas

    # Mostrar una selección para cambiar la clasificación manualmente
    with st.sidebar:
        st.selectbox("Search among all subactivities", key="all_select", options = [''] + all_sub, on_change=guardar)

        contenedores={}
        for clave in dicc_core.keys():
            contenedores[clave] = st.container()
            with contenedores[clave]:
                st.markdown("### {}".format(clave))
                for opcion in dicc_core[clave]:
                    selectbox = creacion_selectbox(opcion['core_activity'])
        
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
            #st.write("Valor cambiado")
        #if boton:
            
            st.success(f'Selected row sort order updated successfully.')
            
            edited_df['Change'] = False
            
            # Limpiar el contenido anterior
            st.empty()

    st.markdown('</div>', unsafe_allow_html=True)
    fin_cambios = st.toggle("Have you finish your changes", label_visibility="visible")
    if fin_cambios:
        finalizar_cambios()


def execute_notebook(notebook_path):
    
    # Lista para almacenar las salidas de las celdas
    output_list = []
    with open(notebook_path, 'r', encoding='utf-8') as script_file:
        python_code = script_file.read()


    # Función para redirigir la salida a Streamlit y capturarla
    class StreamlitOutput:
        def __init__(self):
            self.error_detected = False

        def write(self, text):
            if "AuthenticationError :: Incorrect API key provided" in text:
                self.error_detected = True
                st.error("AuthenticationError :: Incorrect API key provided")
            else:
                output_list.append(text)

    st_output = StreamlitOutput()

    # Redirigir la salida a Streamlit
    original_stdout = sys.stdout
    sys.stdout = st_output

    try:
        # Ejecutar el script Python
        exec(python_code)
        st.write("ha ejecutado el fichero")
    except Exception as e:
        st.error(f'Error al ejecutar el script Python: {e}')
    finally:
        # Restaurar la salida estándar original
        sys.stdout = original_stdout

    # Si se detectó un error, no se muestran las salidas originales
    if not st_output.error_detected:
        for output in output_list:
            st.text(output)


def changed_file():
    # Delete all the items in Session state
    if st.session_state["source_file"]:
        del st.session_state["notebook_ejecutado"]    
        del st.session_state["esperando_resultados"]    
        del st.session_state["batch_size"]    
        if "df" in st.session_state:
            del st.session_state["df"]
        if "df_original" in st.session_state:
            del st.session_state["df_original"]        

st.set_page_config(layout="wide")

dicc_core, dicc_subact, dicc_core_color = load_activities()

all_sub = [f"{s} - {c}" for c in dicc_subact for s in dicc_subact[c]]


# Subir el archivo desde Streamlit
with st.expander("Click for upload"):
    #openai_key = st.text_input("Set OpenAI key", type="password")
    #openai_org = st.text_input("Set OpenAI org", type="password")
    archivo_cargado = st.file_uploader("Upload a file", type=["csv"], key="source_file", on_change=changed_file)

if "notebook_ejecutado" not in st.session_state:
    st.session_state["notebook_ejecutado"] = False

if "esperando_resultados" not in st.session_state:
    st.session_state["esperando_resultados"] = True

if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 10

# Llamar a la función para ejecutar el notebook
mensaje_container = st.empty()
if archivo_cargado is not None and not st.session_state.notebook_ejecutado:

    mensaje_container.write("Loading...")
    filtered_df = clasificacion_core_act.simple_load_file(archivo_cargado)
    if "Zero_shot_classification" not in filtered_df.columns:
        filtered_df['Zero_shot_classification'] = "No work-related"
    mensaje_container.write("File loaded")
    with st.expander("Click here to introduce the API keys"):
        openai_key = st.text_input("Set OpenAI key", type="password")
        openai_org = st.text_input("Set OpenAI org", type="password")
        button_exec = st.button("Click here to classify with the API of OpenAI")

    if openai_key and openai_org and button_exec:
        filtered_df = clasificacion_core_act.load_uploaded_file(archivo_cargado)
        mensaje_container.write(f"Classifying with GPT {len(filtered_df)} elements (it might take a while)...")
        filtered_df = clasificacion_core_act.gpt_classification(filtered_df, openai_key, openai_org)#, mensaje_container)
    
        

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
        print(st.session_state.df['Zero_shot_classification'])
        print(ls)
        ls_subact = []
        for el in ls:
            ls_subact.append(el[0])

        
        st.session_state.df['Subactivity'] = ls_subact#["📊 Data Exploration"]*len(st.session_state.df)
        
        st.session_state.df_original = st.session_state.df

    col00, col01 = st.columns(2)
    with col01:     
        on = st.toggle('Blocks colours')
        on2 = st.toggle('Begin-End colours')
        tiempo_maximo_entre_actividades = st.slider("Maximum time between activities (minutes)", min_value=0, max_value=30, value=5)
    
    with col00:

        df = st.session_state.df_original
        df['Begin'] = pd.to_datetime(df['Begin'], format='%d/%m/%Y %H:%M', errors = 'coerce')  # Asegurarse de que la columna 'Begin' sea de tipo datetime
        distinct_dates = list(df['Begin'].dt.strftime('%d/%m/%Y').unique())
        min_date = df['Begin'].dt.date.min()
        max_date=df['Begin'].dt.date.max()

        st.write(f"Date range: From {min_date} to {max_date}")
        
        a_date = st.date_input("Pick a date", min_value=min_date, max_value=max_date, value=min_date)
        "The date selected:", a_date
        selected_time = st.time_input("Pick a time", value=dt.time(6, 0))
        "Your day starts at:", selected_time
        # Obtener la fecha y hora seleccionadas
        a_datetime = dt.datetime.combine(a_date, selected_time)
        # Calcular la fecha y hora exactas de 24 horas posteriores
        next_day = a_datetime + dt.timedelta(hours=24)

    if on and not on2:
        try:
            st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
            paginate_df('Iris',st.session_state.df, "Estilos")
            clasificar_manualmente(st.session_state.df)            

        except: 
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")

    elif on2:
        try:
            st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
            paginate_df('Iris',st.session_state.df, "Resalto")
            clasificar_manualmente(st.session_state.df)
            

        except:
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")
    else:
        try:
            st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
            paginate_df('Iris',st.session_state.df, "Sin estilos")
            # Ejecutar la función con el DataFrame de ejemplo
            clasificar_manualmente(st.session_state.df)
            
        except: 
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")


