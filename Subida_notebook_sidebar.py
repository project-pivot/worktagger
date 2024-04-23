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
    if s.Zero_shot_classification == "Actively contributing to social debates" :
        return  ['background-color:#FFD1DC']*len(s)
    elif s.Zero_shot_classification == "Assessing the students? assignments and submitting the assessment to the Board of Examiners" :
        return  ['background-color:#FFB6C1']*len(s)
    elif s.Zero_shot_classification == "Adapting a publication" :
        return  ['background-color:#FFD700']*len(s)
    elif s.Zero_shot_classification == "Assessing exams and giving marks" :
        return  ['background-color:#FFECB3']*len(s)
    elif s.Zero_shot_classification == "Communicating about events" :
        return  ['background-color:#FAEBD7']*len(s)
    elif s.Zero_shot_classification == "Communicating to students about the teaching material and assessment" :
        return  ['background-color:#FFA07A']*len(s)
    elif s.Zero_shot_classification == "Conducting research" :
        return  ['background-color:#FFE4C4']*len(s)
    elif s.Zero_shot_classification == "Discussing possible assignments with students" :
        return  ['background-color:#98FB98']*len(s)
    elif s.Zero_shot_classification == "Discussing the structure, provision and progress of the assignment with students" :
        return  ['background-color:#AFEEEE']*len(s)
    elif s.Zero_shot_classification == "Drafting a research plan" :
        return  ['background-color:#B0C4DE']*len(s)
    elif s.Zero_shot_classification == "Drafting conference papers" :
        return  ['background-color:#FFDAB9']*len(s)
    elif s.Zero_shot_classification == "Drafting exam papers" :
        return  ['background-color:#FF6347']*len(s)
    elif s.Zero_shot_classification == "Drafting publications for recognised academic journals and trade journals" :
        return  ['background-color:#DDA0DD']*len(s)
    elif s.Zero_shot_classification == "Encouraging and giving lectures" :
        return  ['background-color:#D8BFD8']*len(s)
    elif s.Zero_shot_classification == "Exploring the societal need for research" :
        return  ['background-color:#E6E6FA']*len(s)
    elif s.Zero_shot_classification == "Following specific courses" :
        return  ['background-color:#F0E68C']*len(s)
    elif s.Zero_shot_classification == "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)":
        return  ['background-color:#FFFAF0']*len(s)
    elif s.Zero_shot_classification == "Organizing national and international travelling" :
        return  ['background-color:#F5DEB3']*len(s)
    elif s.Zero_shot_classification == "Organizing practical aspects for the group" :
        return  ['background-color:#FFF5EE']*len(s)
    elif s.Zero_shot_classification == "Organizing practical aspects of events" :
        return  ['background-color:#FFE4E1']*len(s)
    elif s.Zero_shot_classification == "Participating in group meetings" :
        return  ['background-color:#FAFAD2']*len(s)
    elif  s.Zero_shot_classification == "Periodically discussing research results with fellow researchers and supervisor or co-supervisor" :
        return  ['background-color:#E0FFFF']*len(s)
    elif s.Zero_shot_classification == "Planning teaching activities" :
        return  ['background-color:#FFEBCD']*len(s)
    elif s.Zero_shot_classification == "Preparing and providing teaching sessions for students, providing prospective students with information" :
        return  ['background-color:#FFE4B5']*len(s)
    elif s.Zero_shot_classification == "Proposing events" :
        return  ['background-color:#BC8F8F']*len(s)
    elif s.Zero_shot_classification == "Requesting and assessing leave" :
        return  ['background-color:#F5F5DC']*len(s)
    elif s.Zero_shot_classification == "Reviewing" :
        return  ['background-color:#FFF8DC']*len(s)
    else:
        return ['background-color:#F0FFF0']*len(s)
    
def resaltar_principio_fin_bloques(fila):
    valor_actual_b = fila['Begin']
    valor_actual_e = fila['End']
    valor_actual_e = pd.to_datetime(valor_actual_e, format='%d/%m/%Y %H:%M')
    fila_sig = st.session_state.df_original.iloc[fila.name + 1] if fila.name + 1 < len(st.session_state.df_original) else None
    fila_ant = st.session_state.df_original.iloc[fila.name - 1] if fila.name - 1 >= 0 else None
    if fila_ant is not None:    
        fila_ant['End'] = pd.to_datetime(fila_ant['End'], format='%d/%m/%Y %H:%M')

    #st.write("Valor actual begin", valor_actual_b)
    #st.write("valor actual end", valor_actual_e)
    #st.write("Fila_at", fila_ant)
    #st.write("Fila_sig", fila_sig)
    
    dif_tiempo_ant = (valor_actual_b-fila_ant['End']).total_seconds()/60 if fila_ant is not None else 0
    #st.write("dif_tiempo_ant",dif_tiempo_ant)
    dif_tiempo_sig = (fila_sig['Begin']-valor_actual_e).total_seconds()/60 if fila_sig is not None else 0
    #st.write("dif_tiempo_sig",dif_tiempo_sig)
    ls_estilos = asignar_color(fila)
    if fila_sig is None or dif_tiempo_sig>tiempo_maximo_entre_actividades :
        #st.write("Entra aquí con", fila_sig, "y fila ant", fila_ant)
        ls_estilos[6] = 'background-color:#808080' 
    if fila_ant is None or dif_tiempo_ant>tiempo_maximo_entre_actividades or fila.name==0 :
        #st.write("Entra aquí 2.0 con", fila_sig, "y fila ant", fila_ant)
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
    opciones_clasificacion = [
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
    with st.sidebar:
        contenedor1 = st.container()
        contenedor2= st.container()
        contenedor3 = st.container()

        with contenedor1:
            st.markdown("### Education")
            col0_cont1, col1_cont1 = st.columns(2) 
            for opcion in opciones_clasificacion:
                if opcion == "Assessing the students? assignments and submitting the assessment to the Board of Examiners":
                    with col0_cont1:
                        boton = st.button("Assessing the students?", key=opcion, on_click=guardar, help="Assessing the students? assignments and submitting the assessment to the Board of Examiners")
                        ChangeButtonColour("Assessing the students?", 'black', '#FFB6C1')
                elif opcion == "Assessing exams and giving marks":
                    with col1_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFECB3')
                        
                elif opcion == "Communicating to students about the teaching material and assessment":
                    with col0_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFA07A')
                elif opcion == "Discussing the structure, provision and progress of the assignment with students":
                    with col1_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#AFEEEE')
                        
                elif opcion == "Discussing possible assignments with students":
                    with col0_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#98FB98')
                elif opcion == "Drafting exam papers":
                    with col1_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FF6347')
                elif opcion == "Encouraging and giving lectures":
                    with col0_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#D8BFD8')
                elif opcion == "Planning teaching activities":
                    with col1_cont1:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFEBCD')
                elif opcion == "Preparing and providing teaching sessions for students, providing prospective students with information":
                    with col1_cont1:
                        boton = st.button("Preparing and providing teaching sessions", key=opcion, on_click=guardar, help="Preparing and providing teaching sessions for students, providing prospective students with information")
                        ChangeButtonColour("Preparing and providing teaching sessions", 'black', '#FFE4B5')
                            

        with contenedor2: 
            st.markdown("### Research")
            col0_cont2, col1_cont2 = st.columns(2)
            for opcion in opciones_clasificacion:
                if opcion == "Adapting a publication":
                    with col0_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFD700')
                elif opcion == "Conducting research":
                    with col1_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFE4C4')
                elif opcion == "Drafting a research plan":
                    with col0_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#B0C4DE')
                elif opcion == "Drafting conference papers":
                    with col1_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFDAB9')
                elif opcion == "Drafting publications for recognised academic journals and trade journals":
                    with col0_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#DDA0DD')
                
                elif opcion =="Exploring the societal need for research":
                    with col0_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#E6E6FA')
                elif opcion =="Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)":
                    with col1_cont2:
                        boton = st.button("Initiating a new research project", key=opcion, on_click=guardar)
                        ChangeButtonColour("Initiating a new research project", 'black', '#FFFAF0')
                elif opcion =="Periodically discussing research results with fellow researchers and supervisor or co-supervisor":
                    with col0_cont2:
                        boton = st.button("Periodically discussing research results", key=opcion, on_click=guardar, help ="Periodically discussing research results with fellow researchers and supervisor or co-supervisor")
                        ChangeButtonColour("Periodically discussing research results", 'black', '#E0FFFF')
                elif opcion == "Reviewing":
                    with col1_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFF8DC')
                elif opcion == "Supervising and discussing the progress of the partial or completed research with PhD candidates":
                    with col1_cont2:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#F0FFF0')



                


        with contenedor3:
            st.markdown("#### Other")
            col0_cont3, col1_cont3 = st.columns(2)
            for opcion in opciones_clasificacion:
                if opcion =="Actively contributing to social debates":
                    with col0_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFD1DC')
                elif opcion =="Communicating about events":
                    with col1_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar) 
                        ChangeButtonColour(opcion, 'black', '#FAEBD7')
                elif opcion == "Following specific courses":
                    with col0_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#F0E68C')
                elif opcion =="Organizing national and international travelling":
                    with col0_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#F5DEB3')
                elif opcion =="Organizing practical aspects for the group":
                    with col1_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFF5EE')

                elif opcion == "Organizing practical aspects of events":
                    with col0_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FFE4E1')

                elif opcion =="Participating in group meetings":
                    with col1_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#FAFAD2')

                elif opcion =="Proposing events":
                    with col1_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#BC8F8F')

                elif opcion =="Requesting and assessing leave":
                    with col1_cont3:
                        boton = st.button(opcion, key=opcion, on_click=guardar)
                        ChangeButtonColour(opcion, 'black', '#F5F5DC')
                

        
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
            
            st.success(f'Clasificación para las filas seleccionadas actualizada exitosamente.')
            
            edited_df['Change'] = False
            
            # Limpiar el contenido anterior
            st.empty()

    st.markdown('</div>', unsafe_allow_html=True)


def execute_notebook(notebook_path):
    
    # Lista para almacenar las salidas de las celdas
    output_list = []

    # Cargar el notebook
    with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
        notebook_content = nbformat.read(notebook_file, as_version=4)

    # Configurar el exportador para convertir a Python
    exporter = PythonExporter()
    exporter.exclude_output = False

    # Convertir el notebook a un script de Python
    python_code, _ = exporter.from_notebook_node(notebook_content)

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
notebook_path = 'prueba_subida.ipynb'

if "notebook_ejecutado" not in st.session_state:
    st.session_state["notebook_ejecutado"] = False

if "esperando_resultados" not in st.session_state:
    st.session_state["esperando_resultados"] = True

if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 10

#esperando_resultados = True
#notebook_ejecutado = False
# Llamar a la función para ejecutar el notebook
mensaje_container = st.empty()
if archivo_cargado is not None and not st.session_state.notebook_ejecutado:
    #st.write("Vuelve a entrar y a ejecutar notebook")

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
    #st.text("¡Los resultados están listos!")
    #st.markdown("### Resultado del Notebook")
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

        #st.markdown("### Date range")
        df = st.session_state.df_original
        df['Begin'] = pd.to_datetime(df['Begin'], format='%d/%m/%Y %H:%M')  # Asegurarse de que la columna 'Begin' sea de tipo datetime
        distinct_dates = list(df['Begin'].dt.strftime('%d/%m/%Y').unique())
        min_date = df['Begin'].dt.date.min()
        max_date=df['Begin'].dt.date.max()
        

        #a_date = st.date_input("Pick a date",selectable_dates = distinct_dates, value=min_date)
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
            #st.session_state.df =  df[df['Begin'].dt.date == a_date]
            paginate_df('Iris',st.session_state.df, "Estilos")
            clasificar_manualmente(st.session_state.df)

        except: 
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")

    elif on2:
        try:
            st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
            #st.session_state.df = df[df['Begin'].dt.date == a_date]
            paginate_df('Iris',st.session_state.df, "Resalto")
            clasificar_manualmente(st.session_state.df)

        except:
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")
    else:
        try:
            st.session_state.df = df[(df['Begin'] >= a_datetime) & (df['Begin'] < next_day)]
            #st.session_state.df = df[df['Begin'].dt.date == a_date]
            paginate_df('Iris',st.session_state.df, "Sin estilos")
            # Ejecutar la función con el DataFrame de ejemplo
            clasificar_manualmente(st.session_state.df)
            
            
        except: 
            st.error("There is no data for the selected date 😞. Why don't you try with another one? 😉")



        
    

    # Aquí puedes continuar con el procesamiento o la visualización de los resultados
#else:
    # El tiempo de espera ha superado el límite, mostrar mensaje de advertencia
#    st.warning("El tiempo de espera ha superado los 5 minutos y el archivo resultado aún no está disponible.")

