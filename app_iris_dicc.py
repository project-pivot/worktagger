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


#Diccionario cuya clave es el nombre de la actividad y el valor es el color que se le asigna a dicha actividad
dicc_class = {
    "Actively contributing to social debates":'#FFD1DC',
    "Assessing the students? assignments and submitting the assessment to the Board of Examiners":'#FFB6C1',
    "Adapting a publication":'#FFD700',
    "Assessing exams and giving marks":'#FFECB3',
    "Communicating about events":'#FAEBD7',
    "Communicating to students about the teaching material and assessment":'#FFA07A',
    "Conducting research":'#FFE4C4',
    "Discussing possible assignments with students":'#98FB98',
    "Discussing the structure, provision and progress of the assignment with students":'#AFEEEE',
    "Drafting a research plan":'#B0C4DE',
    "Drafting conference papers": '#FFDAB9',
    "Drafting exam papers":'#FF6347',
    "Drafting publications for recognised academic journals and trade journals":'#DDA0DD',
    "Encouraging and giving lectures":'#D8BFD8',
    "Exploring the societal need for research":'#E6E6FA',
    "Following specific courses":'#F0E68C',
    "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)":'#FFFAF0',
    "Organizing national and international travelling": '#F5DEB3',
    "Organizing practical aspects for the group": '#FFF5EE',
    "Organizing practical aspects of events":'#FFE4E1',
    "Participating in group meetings":'#FAFAD2',
    "Periodically discussing research results with fellow researchers and supervisor or co-supervisor":'#E0FFFF',
    "Planning teaching activities":'#FFEBCD',
    "Preparing and providing teaching sessions for students, providing prospective students with information":'#FFE4B5',
    "Proposing events":'#BC8F8F',
    "Requesting and assessing leave":'#F5F5DC',
    "Reviewing":'#FFF8DC',
    "Supervising and discussing the progress of the partial or completed research with PhD candidates":'#F0FFF0'

}

dicc_botones_largos = {"Assessing the students? assignments and submitting the assessment to the Board of Examiners":"Assessing the students?",
                  "Preparing and providing teaching sessions for students, providing prospective students with information":"Preparing and providing teaching sessions",
                  "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)":"Initiating a new research project",
                  "Periodically discussing research results with fellow researchers and supervisor or co-supervisor": "Periodically discussing research results" 
                  }


ls_educ = ["Assessing the students? assignments and submitting the assessment to the Board of Examiners",
           "Assessing exams and giving marks",
           "Communicating to students about the teaching material and assessment",
           "Discussing the structure, provision and progress of the assignment with students",
           "Discussing possible assignments with students",
           "Drafting exam papers",
           "Encouraging and giving lectures",
           "Planning teaching activities",
           "Preparing and providing teaching sessions for students, providing prospective students with information"
           ]

ls_research = ["Adapting a publication",
               "Conducting research",
               "Drafting a research plan",
               "Drafting conference papers",
               "Drafting publications for recognised academic journals and trade journals",
               "Exploring the societal need for research",
               "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)",
               "Periodically discussing research results with fellow researchers and supervisor or co-supervisor",
               "Reviewing",
               "Supervising and discussing the progress of the partial or completed research with PhD candidates"
               ]

ls_other = ["Actively contributing to social debates",
            "Communicating about events",
            "Following specific courses",
            "Organizing national and international travelling",
            "Organizing practical aspects for the group",
            "Organizing practical aspects of events",
            "Participating in group meetings",
            "Proposing events",
            "Requesting and assessing leave"
            ]


st.set_page_config(layout="wide")
# Subir el archivo desde Streamlit
with st.expander("Click for upload"):
    key = st.text_input("Set OpenAI key", type="password")
    org = st.text_input("Set OpenAI org", type="password")
    if key and org:
        # Crear un DataFrame con los valores
        data_openai = {'Key': [key], 'Organization': [org]}
        df_openai = pd.DataFrame(data_openai)
    
        # Guardar el DataFrame en un archivo CSV
        df_openai.to_csv('openai_config.csv', index=False)
    archivo_cargado = st.file_uploader("Upload a file", type=["csv"])


def creacion_botones(col0, col1, counter,option):
    if counter%2 == 0:
        with col0:

            if option in dicc_botones_largos:
                boton = st.button(dicc_botones_largos[option], key=option, on_click=guardar, help = option)
                ChangeButtonColour(dicc_botones_largos[option], 'black', dicc_class[option])
            else:
                boton = st.button(option, key=option, on_click=guardar)
                ChangeButtonColour(option, 'black', dicc_class[option])


    else:
        with col1:
            if option in dicc_botones_largos:
                boton = st.button(dicc_botones_largos[option], key=option, on_click=guardar, help = option)
                ChangeButtonColour(dicc_botones_largos[option], 'black', dicc_class[option])
            else:
                boton = st.button(option, key=option, on_click=guardar)
                ChangeButtonColour(option, 'black', dicc_class[option])

    return boton


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


def guardar():
    df_original = st.session_state.df_original
    seleccion = [clave for clave,valor in st.session_state.items() if pd.api.types.is_bool(valor) and valor==True and clave!="notebook_ejecutado" and clave!="esperando_resultados"]
    filas_seleccionadas = st.session_state.filas_seleccionadas
    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Zero_shot_classification'] = seleccion*len(filas_seleccionadas)

def finalizar_cambios():
    df = st.session_state.df
    df.to_excel("DataFrame_Final.xlsx", index=False)
    st.success("Cambios finalizados. DataFrame guardado en 'DataFrame_Final.xlsx")

def asignar_color(s):
    col = dicc_class[s.Zero_shot_classification]
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

    # Mostrar la interfaz de edición
    edited_df = st.data_editor(
        df,
        column_config={
            "Change": st.column_config.CheckboxColumn(
                "Change",
                help="Elige las filas a las que haya que cambiar su clasificación",
                default=False,
            ),
            "Begin": None,
            "End": None,
            "ID": None,
            '':None

        },
        disabled=["ID", 'Merged_titles', 'Begin', 'End','Begin Time','Ending Time', 'App', 'Type', 'Duration', 'Most_occuring_title', 'Zero_shot_classification'],
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
        contenedor1 = st.container()
        contenedor2= st.container()
        contenedor3 = st.container()

        with contenedor1:
            st.markdown("### Education")
            col0_cont1, col1_cont1 = st.columns(2)
            cont_educ = 0
            for opcion in ls_educ:
                boton = creacion_botones(col0_cont1,col1_cont1, cont_educ, opcion) 
                cont_educ= cont_educ+1             

        with contenedor2: 
            st.markdown("### Research")
            col0_cont2, col1_cont2 = st.columns(2)
            cont_research = 0
            for opcion in ls_research:
                boton = creacion_botones(col0_cont2,col1_cont2, cont_research, opcion) 
                cont_research= cont_research+1   

        with contenedor3:
            st.markdown("#### Other")
            col0_cont3, col1_cont3 = st.columns(2)
            cont_other = 0
            for opcion in ls_other:
                boton = creacion_botones(col0_cont3,col1_cont3, cont_other, opcion) 
                cont_other= cont_other+1   
                
        
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

        if boton:
            
            st.success(f'Selected row sort order updated successfully.')
            
            edited_df['Change'] = False
            
            # Limpiar el contenido anterior
            st.empty()

    st.markdown('</div>', unsafe_allow_html=True)


def execute_notebook(notebook_path):
    
    # Lista para almacenar las salidas de las celdas
    output_list = []
    with open(notebook_path, 'r', encoding='utf-8') as script_file:
        python_code = script_file.read()
    # Cargar el notebook
    #with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
    #    notebook_content = nbformat.read(notebook_file, as_version=4)

    # Configurar el exportador para convertir a Python
    #exporter = PythonExporter()
    #exporter.exclude_output = False

    # Convertir el notebook a un script de Python
    #python_code, _ = exporter.from_notebook_node(notebook_content)

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
    except Exception as e:
        st.error(f'Error al ejecutar el script Python: {e}')
    finally:
        # Restaurar la salida estándar original
        sys.stdout = original_stdout

    # Si se detectó un error, no se muestran las salidas originales
    if not st_output.error_detected:
        for output in output_list:
            st.text(output)

# Ruta al notebook que quieres ejecutar
#notebook_path = 'Notebook_Iris.ipynb'
#notebook_path = 'prueba_subida.py'
notebook_path = "clasificacion_iris.py"

if "notebook_ejecutado" not in st.session_state:
    st.session_state["notebook_ejecutado"] = False

if "esperando_resultados" not in st.session_state:
    st.session_state["esperando_resultados"] = True

if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 10


# Llamar a la función para ejecutar el notebook
mensaje_container = st.empty()
if archivo_cargado is not None and not st.session_state.notebook_ejecutado:


    mensaje_container.write("Notebook running...")

    with open("archivo_temporal.csv", "wb") as f:
        f.write(archivo_cargado.read())
    inicio_espera = time.time()
    execute_notebook(notebook_path)
    mensaje_container.empty()
    # Ruta del archivo de resultados
    ruta_resultado = "resultados.xlsx"
    st.session_state.notebook_ejecutado = True

    # Tiempo máximo de espera en segundos
    tiempo_maximo_espera = 300  # 5 minutos

    # Tiempo inicial
    inicio_espera = time.time()

    # Bucle de espera dinámica
    while (time.time() - inicio_espera) < tiempo_maximo_espera:
        # Verificar si el archivo de resultados existe
        if os.path.exists(ruta_resultado):
            # El archivo ha sido encontrado, salir del bucle
            st.session_state.esperando_resultados = False
            break
    
        # Calcular el tiempo restante de espera
        tiempo_restante = tiempo_maximo_espera - (time.time() - inicio_espera)
    
        # Mostrar mensaje de progreso al usuario
        st.text(f"Esperando resultados... Tiempo restante: {int(tiempo_restante)} segundos")
    
        # Esperar un segundo antes de volver a verificar
        time.sleep(1)


# Verificar si se encontró el archivo de resultados
if not st.session_state.esperando_resultados:
    # El archivo de resultados ha sido encontrado, mostrar mensaje de éxito

    if "df" not in st.session_state:
        data = pd.read_excel(ruta_resultado)
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
        st.session_state.df_original = st.session_state.df

    col00, col01 = st.columns(2)
    with col01:     
        on = st.toggle('Blocks colours')
        on2 = st.toggle('Begin-End colours')
        tiempo_maximo_entre_actividades = st.slider("Maximum time between activities (minutes)", min_value=0, max_value=30, value=5)
    
    with col00:

        df = st.session_state.df_original
        df['Begin'] = pd.to_datetime(df['Begin'], format='%d/%m/%Y %H:%M')  # Asegurarse de que la columna 'Begin' sea de tipo datetime
        distinct_dates = list(df['Begin'].dt.strftime('%d/%m/%Y').unique())
        min_date = df['Begin'].dt.date.min()
        max_date=df['Begin'].dt.date.max()
        
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


