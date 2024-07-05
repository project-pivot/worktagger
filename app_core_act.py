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


dicc_core = {
    "General": [{
        "core_activity": "Faculty plan/capacity group plan", 
        "color" : "#FFB6C1", 
        "activities": [
        "Setting out long-term policies for the chair, both in technical terms (research and education) as well as with regard to its social significance and added value (valorisation)",
        "Analysing the resources available (both internal and external) for research and education in terms of FTE for the coming academic year",
        "Reading trade journals, visiting conferences and maintaining relations with fellow researchers"
        ]
        },
        {
            "core_activity": "Management of education and research", 
            "color": "#FFD700",
            "activities": [
                "Maintaining and developing relationships and contacts within the various scientific networks",
                "Fostering national and international cooperation with other faculties, universities and other partners in society",
                "Consulting with the Capacity Group Chairman on the progress of education and research within the chair and to take action or make suitable changes"
            ] 
        },
        {
            "core_activity": "Human Resources policy",
            "color": '#FFA07A',
            "activities": [
                "Contributing to the recruitment and selection of employees",
                "Conducting performance assessment interviews with employees of the chair",
                "Development of talent and professionalisation of employees",
                "Following a course for personal development",
                "Coaching and supervision of employees of the chair",
                "Sharing information from the various consultation bodies with the employees of the chair"
            ]
        },
        {
            "core_activity": "Organizational matters",
            "color": "#AFEEEE",
            "activities": [
                "Requesting and assessing leave",
                "Claiming and assessing expenses",
                "Reporting sickness",
                "Salary slip inspection",
                "Requesting coaching/intervision/mentoring",
                "Preparing and discussing official performance assessments",
                "Solving / finding help for small issues"
            ]
        },
        {
            "core_activity": "Programme development",
            "color": "#98FB98",
            "activities": [
                "Monitoring relevant national and international developments in their own field of education",
                "Conducting analyses, or having analyses conducted, of educational needs in society and the learning needs of students",
                "Ensuring the selection of relevant literature and teaching methodologies",
                "Ensuring that relevant developments are translated into one or more course components and that these are submitted to the Programme Committee for approval",
                "Ensuring the preparation of teaching materials, assignments, questions for exams and examinations"
            ]
        },
        {
            "core_activity":"Acquisition of contract teaching and research",
            "color": "#FF6347",
            "activities": [
                "Initiating development of non-subsidised education",
                "Exploring the external market for funding as well as the requirements of external potential partners or funders",
                "Negotiating with external parties regarding the requirements for contract research and education and drafting and submitting proposals to external parties",
                "Developing and maintaining contacts with leading researchers and research and education funders",
                "Stimulating employees of the chair to apply for external funding",
                "Acquiring grants and encouraging employees to apply for external funding",
                "Contributing to the development of non-subsidised education",
                "Identifying relevant developments and potential opportunities in the field of education and research" 
            ]
        },
        {
            "core_activity": "Accountability for contract teaching and research",
            "color":"#D8BFD8",
            "activities":[
                "Reporting to the client regarding implementation and results",
                "Discussing progress and reports thereof with those parties implementing contract teaching and research",
                "Making appropriate changes to contract teaching and research if there are discrepancies regarding the contract requirements in terms of funding, duration, planning and objectives"

            ]
        },
        {
            "core_activity":"Advancing/communicating scientific knowledge and insight",
            "color":"#FFEBCD",
            "activities":[ 
                "Creating and advancing networks aimed at the dissemination of knowledge and insight",
                "Initiating national and international collaboration opportunities with other faculties, universities and other partners in society",
                "Actively contributing to social debates",
                "Encouraging and giving lectures",
                "Encouraging and giving interviews for various media outlets",
                "Exploring and responding to the needs for new research expressed by society"

            ]
        },
        {
            "core_activity": "Working groups and committees",
            "color":"#FFE4B5",
            "activities":[ 
                "Preparing the topics to be discussed within the relevant working groups or committees",
                "Participating in or leading the meetings of the committees and working groups",
                "Elaborating certain issues and topics in preparation of a future meeting",
                "Keeping the employees within the chair informed of the issues discussed within the working groups"
            ]
        },
        {
            "core_activity": "Contribution to the research group or lab",
            "color":"#FFD700",
            "activities":[ 
                "Participating in group meetings",
                "Organizing practical aspects for the group",
                "Keeping members up-to-date with relevant information regarding organization, research or education"
            ]
        },
        {
            "core_activity": "Organization of (series of) events",
            "color":"#FFE4C4",
            "activities":[ 
                "Proposing events",
                "Organizing practical aspects of events",
                "Communicating about events"
            ]
        }
    ],
                                                                                                          
    "Education": [
        {
            "core_activity": "Provision of education",
            "color":"#B0C4DE",
            "activities":[ 
                "Ensuring the preparation and provision of assigned course components",
                "Ensuring the evaluation and, where necessary, adjustment of assigned course components",
                "Ensuring the integration of research results in education",
                "Ensuring the application of the quality system",
                "Coordinating with the Director of the teaching institute on the staffing for the provision of the assigned course components",
                "Integrating research results into the curriculum",
                "Preparing and providing teaching sessions for students, providing prospective students with information",
                "Creating the right conditions for the learning process by applying didactic teaching methods",
                "Supervising and coaching students during teaching sessions in the learning process",
                "Supervising and assessing work placement and final projects and theses of students",
                "Preparing practicals, tutorials and pre-structured lectures, etc.",
                "Providing practicals, tutorials and pre-structured lectures, etc.",
                "Co-authoring and assessing assignments and papers in a teaching context"
            ]
        },
        {
            "core_activity":"Student supervision",
            "color":"#FFDAB9",
            "activities":[ 
                "Discussing possible assignments with students",
                "Discussing the structure, provision and progress of the assignment with students",
                "Assessing the students’ assignments and submitting the assessment to the Board of Examiners",
                "Determining the integration of graduation subjects within the research plan with students",
                "Providing input for the assessment of graduating students",
                "Discussing the progress of research with students",
                "Assisting with the correcting of theses, graduation projects and reports"
                
            ]
        },
        {
            "core_activity":"PhD candidates",
            "color":"#DDA0DD",
            "activities":[ 
                "Informing PhD candidates on possible doctoral thesis subjects",
                "Hiring PhD candidates for doctoral research",
                "Supervising and discussing the progress of the partial or completed research with PhD candidates",
                "Assessing the thesis of the PhD candidate",
                "Testing the training programmes set up by PhD candidates against the requirements of the policy on PhD candidates and the requirements of the National Graduate School if participation is taking place in this",
                "Providing the supervisor with input for the assessment of PhD candidates",
                "Supervising PhD candidates in the preparation and provision of a course component to be taught together and providing relevant"
                
            ]
        },
        {
            "core_activity": "Education development",
            "color":"#E6E6FA",
            "activities":[ 
                "Monitoring relevant national and international developments in their own field of education",
                "Analysing the educational needs of society and students’ learning needs",
                "Creating formats for new or adapting existing course components based on relevant developments in coordination with relevant colleagues",
                "Selecting relevant literature and teaching methods",
                "Creating or adapting teaching materials and assignments"
                
            ]
        },
        {
            "core_activity": "Testing",
            "color":"#FFFAF0",
            "activities":[
                "Creating formats for new or adapting existing exam questions based on relevant developments",
                "Administering both oral and written exams",
                "Assessing exams and giving marks",
                "Drafting exam papers" 
                
            ]
        },
        {
            "core_activity": "Education evaluation",
            "color":"#E0FFFF",
            "activities":[ 
                "Evaluating and adjusting their course components where necessary",
                "Drafting and implementing improvement proposals for their own course components and any related course components",
                "Participating in internal working groups and discussions regarding education evaluation",
                "Analysing the provision of course components with students and lecturers",
                "Contributing to evaluation reports regarding the format and provision of the curriculum or components thereof",
                "Collecting information for external education review committees",
                "Providing information to external education review committees",
                "Providing information to teaching assessment panels"
                
            ]
        },
        {
            "core_activity": "Education coordination",
            "color":"#FFF8DC",
            "activities":[ 
                "Encouraging the alignment of the development and execution of course components",
                "Improving cohesion, both in terms of methodology and content, between course components",
                "Assigning job assignments and giving instructions as well as monitoring the progress and quality of their execution by academic and teaching support staff",
                "Cooperating in the recruitment, selection and assessment of teaching support staff",
                "Communicating to students about the teaching material and assessment",
                "Planning teaching activities",
                "Aligning with other courses",
                "Assessing student admission portfolios",
                "Assessing scholarship applications",
                "Assessing hardship appeals",
                "Participating in educational marketing events",
                "Updating programme website texts",
                "Assessing suitability and quality of theses for thesis award",
                "Realizing collegial course transferral"
            ]
        }
        

    ],
    "Research":[
        {
            "core_activity":"Research development",
            "color":"#F0FFF0",
            "activities":[ 
                "Monitoring relevant national and international scientific developments in the chair's research field",
                "Exploring and assessing the societal need for research and the opportunities for valorisation of that research",
                "Creating initiatives for new research programme in consultation with relevant national and international colleagues (and external parties) based on consideration of the various developments (scientific content, societal needs, opportunities for valorisation)",
                "Ensuring the translation of a research programme into research projects",
                "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)",
                "Drafting a research plan"
            ]
        },
        {
            "core_activity": "Assessment of research",
            "color":"#FFD1DC",
            "activities":[ 
                "Assessing doctoral theses (national or international)",
                "Reviewing journal and conference papers",
                "Organizing national and international travelling"
                
            ]
        },
        {
            "core_activity": "Execution of research",
            "color":"#FAEBD7",
            "activities":[ 
                "Conducting research",
                "Driving and managing academic and research support staff",
                "Ensuring the application of the quality system in respect of the research",
                "Monitoring the academic integrity of the research in respect of external stakeholders",
                "Drafting publications and giving lectures at national and international conferences",
                "Consulting with the chair of the capacity group regarding progress of research within the chair and taking action to calibrate efforts on that basis",
                "coordinating with the Director of the research institute regarding the staffing to be provided for the execution of the research",
                "Coordinating the research question and working hypotheses with the (associate) Professor",
                "Creating a literature review, attending symposiums and conferences and discussions with experts",
                "Formulating the research question, working hypotheses and specifying the research data required, research methods and target groups",
                "Exchanging knowledge with fellow national and international researchers and experts",
                "Safeguarding the academic integrity of the research"
            ]
        },
        {
            "core_activity": "Publication of research",
            "color":"#c1e6c2",
            "activities":[ 
                "Drafting publications for recognised academic journals and trade journals",
                "Drafting conference papers and giving lectures at conferences",
                "Giving presentations at external organisations",
                "Adapting the publication following responses from reviewers and fellow researchers",
                "Making agreements with external parties, if present, regarding the publication of research results",
                "Organizing national and international travelling"
            ]
        },
        {
            "core_activity": "Research coordination",
            "color":"#F0E68C",
            "activities":[ 
                "Structuring the research in research subquestions",
                "Encouraging coordination between substudies",
                "Improving the cohesion, both in terms of methodology and content, between substudies",
                "Assigning job assignments and giving instructions as well as monitoring the progress and quality of their execution by academic and research support staff",
                "Participating in the recruitment, selection and assessment of research support staff",
                "Coordinating with other research or substudies",
                "Assigning responsibilities and giving instructions to academic and research support staff",
                "Monitoring the progress and quality of the execution of job assignments issued to academic and research support staff"
            ]
        },
        {
            "core_activity": "Research proposal",
            "color":"#F5DEB3",
            "activities":[ 
                "Becoming informed on subject matter by a literature review, attending symposiums, conducting interviews with experts",
                "Following specific courses",
                "Formulating a research question",
                "Co-authoring research proposals for further research"

            ]
        },
        {
            "core_activity": "Research plan",
            "color":"#FFF5EE",
            "activities":[ 
                "Becoming familiar with existing methodologies",
                "Formulating working hypotheses and specifying the necessary research data",
                "Exchanging knowledge with fellow researchers and subject matter experts",
                "Making agreements with target groups and stakeholders",
                "Drafting and coordinating the schedule and action plan with the supervisor/committee of the research institute/the research school",
            ]
        },
        {
            "core_activity": "Performing research",
            "color":"#FFE4E1",
            "activities":[ 
                "Contributing knowledge to research by others within the capacity group",
                "Assessing the quality of the research data collected",
                "Documenting the data in a research journal",
                "Updating and calibrating research methodologies and research instruments",
                "Periodically discussing research results with fellow researchers and supervisor or co-supervisor"
            ]
        },
        {
            "core_activity": "Doctoral thesis",
            "color":"#FAFAD2",
            "activities":[ 
                "Writing draft chapters",
                "Discussing any draft chapters with the supervisor or co-supervisors",
                "Amending drafts",
                "Responding to the questions of the Doctoral Committee"
            ]
        }

    ]
}

if "openai_key" not in st.session_state:
    st.session_state.openai_key = None
if "openai_org" not in st.session_state:
    st.session_state.openai_org = None
if "archivo_cargado" not in st.session_state:
    st.session_state.archivo_cargado = None

#Returns a dictionary where the key is the name of the core activity and the value is the list of corresponding subactivities
def create_dicc_subactivities(dicc):
    new_dicc_core = {}
    for key in dicc:
        for aux_dicc in dicc[key]:
            core_activity = aux_dicc['core_activity']
            subactivities = aux_dicc['activities']
            new_dicc_core[core_activity] = subactivities
    return new_dicc_core
dicc_subact = create_dicc_subactivities(dicc_core)



def create_dicc_color(dicc):
    new_dict_color={}

    for key in dicc:
        for aux_dict in dicc[key]:
            act = aux_dict["core_activity"]
            color = aux_dict["color"]
            new_dict_color[act] = color
            
    return new_dict_color

dicc_core_color = create_dicc_color(dicc_core)

def get_subactivity_options(row):
    classification = row['Zero_shot_classification']
    return dicc_subact.get(classification, [])

st.set_page_config(layout="wide")



# Subir el archivo desde Streamlit
with st.expander("Click for upload"):
    st.session_state.openai_key = st.text_input("Set OpenAI key", type="password")
    st.session_state.openai_org = st.text_input("Set OpenAI org", type="password")
    #if st.session_state.key and st.session_state.org:
        # Crear un DataFrame con los valores
        #data_openai = {'Key': [key], 'Organization': [org]}
        #df_openai = pd.DataFrame(data_openai)
    
        # Guardar el DataFrame en un archivo CSV
        #df_openai.to_csv('openai_config.csv', index=False)
    st.session_state.archivo_cargado = st.file_uploader("Upload a file", type=["csv"])
    #st.write("archivo cargado", archivo_cargado)

def creacion_selectbox(col0, col1, counter,option):
    if counter%2== 0:
        with col0:
            selectbox = st.selectbox(option, key=option, options = [''] + dicc_subact[option], on_change=guardar)
            ChangeSelectBoxColour(option,'black', dicc_core_color[option])
    else:
        with col1:
            selectbox = st.selectbox(option, key=option, options =[''] + dicc_subact[option], on_change=guardar)
            ChangeSelectBoxColour(option, 'black', dicc_core_color[option])


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
    


def guardar():
    df_original = st.session_state.df_original
    seleccion_core_act = [clave for clave, valor in st.session_state.items() if isinstance(valor, str) and valor != "" and valor !="all day" and clave!="openai_key" and clave!="openai_org"]
    seleccion_subact = [valor for clave, valor in st.session_state.items() if isinstance(valor, str) and valor != "" and valor!="all day" and clave!="openai_key" and clave!="openai_org"]
    filas_seleccionadas = st.session_state.filas_seleccionadas
    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Subactivity'] = seleccion_subact*len(filas_seleccionadas)
    df_original.loc[df['ID'].isin(filas_seleccionadas), 'Zero_shot_classification'] = seleccion_core_act*len(filas_seleccionadas)
   
    reset()
    

def finalizar_cambios():
    df = st.session_state.df
    df.to_excel("DataFrame_Final.xlsx", index=False)
    st.success("Cambios finalizados. DataFrame guardado en 'DataFrame_Final.xlsx")

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
        contenedores={}
        for clave in dicc_core.keys():
            contenedores[clave] = st.container()
            cont_cat = 0
            with contenedores[clave]:
                st.markdown("### {}".format(clave))
                col0_cont, col1_cont = st.columns(2)
                for opcion in dicc_core[clave]:
                    selectbox = creacion_selectbox(col0_cont,col1_cont, cont_cat, opcion['core_activity'])
                    #boton = creacion_botones(col0_cont,col1_cont, cont_cat, opcion['core_activity'])
                    cont_cat = cont_cat+1 
        
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

# Ruta al notebook que quieres ejecutar
#notebook_path = 'prueba_subida.py'
notebook_path = "clasificacion_core_act.py"

if "notebook_ejecutado" not in st.session_state:
    st.session_state["notebook_ejecutado"] = False

if "esperando_resultados" not in st.session_state:
    st.session_state["esperando_resultados"] = True

if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 10


# Llamar a la función para ejecutar el notebook
mensaje_container = st.empty()
if st.session_state.archivo_cargado is not None and not st.session_state.notebook_ejecutado:


    mensaje_container.write("Notebook running...")

    #with open("archivo_temporal.csv", "wb") as f:
    #    f.write(archivo_cargado.read())
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
        ls =  st.session_state.df['Zero_shot_classification'].map(dicc_subact)
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


