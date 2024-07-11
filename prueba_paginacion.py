import streamlit as st

# Inicializamos el valor compartido en el session state
if 'shared_value' not in st.session_state:
    st.session_state.shared_value = 0

# Función para actualizar el valor compartido desde Input 1
def update_from_input1():
    st.session_state.shared_value = st.session_state.input1
    st.session_state.input2 = st.session_state.shared_value

# Función para actualizar el valor compartido desde Input 2
def update_from_input2():
    st.session_state.shared_value = st.session_state.input2
    st.session_state.input1 = st.session_state.shared_value

# Input 1
if 'input1' not in st.session_state:
    st.session_state.input1 = 1
st.number_input('Input 1', value=st.session_state.input1, key='input1', on_change=update_from_input1)

# Input 2
if 'input2' not in st.session_state:
    st.session_state.input2 = 1
st.number_input('Input 2', value=st.session_state.input2, key='input2', on_change=update_from_input2)

# Mostrar los valores de ambos inputs
st.write(f"Valor de Input 1: {st.session_state.input1}")
st.write(f"Valor de Input 2: {st.session_state.input2}")
