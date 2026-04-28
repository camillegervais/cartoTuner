import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.io import loadmat
import numpy as np
from data_input_processing import *

st.set_page_config(layout="wide")

# Sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Sélectionner un fichier")
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        # Load MAT file
        mat_data = loadmat(uploaded_file)
        mat_data = clean_input_data(mat_data)
        st.session_state['mat_data'] = mat_data
        st.write("Fichier chargé :", uploaded_file.name)
        st.write("Variables disponibles :", list(mat_data.keys()))

# Main area
st.title("Carto Tuner")

# Inputs for table size
col1, col2 = st.columns(2)
with col1:
    num_rows = st.number_input("Nombre de lignes", min_value=1, value=5, step=1)
with col2:
    num_cols = st.number_input("Nombre de colonnes", min_value=1, value=5, step=1)

# Adjust row and column names values lengths
if 'row_names_values' not in st.session_state or len(st.session_state['row_names_values']) != num_rows:
    current = st.session_state.get('row_names_values', [])
    if len(current) < num_rows:
        current += [0.0] * (num_rows - len(current))
    else:
        current = current[:num_rows]
    st.session_state['row_names_values'] = current

if 'col_names_values' not in st.session_state or len(st.session_state['col_names_values']) != num_cols:
    current = st.session_state.get('col_names_values', [])
    if len(current) < num_cols:
        current += [0.0] * (num_cols - len(current))
    else:
        current = current[:num_cols]
    st.session_state['col_names_values'] = current

# Row names table
row_names_df = pd.DataFrame([st.session_state['row_names_values']], columns=[f'Row {i+1}' for i in range(num_rows)])
st.subheader("Valeurs des noms de lignes")
edited_row_names = st.data_editor(row_names_df, width='stretch')
st.session_state['row_names_values'] = list(edited_row_names.iloc[0])


# Column names table
col_names_df = pd.DataFrame([st.session_state['col_names_values']], columns=[f'Col {i+1}' for i in range(num_cols)])
st.subheader("Valeurs des noms de colonnes")
edited_col_names = st.data_editor(col_names_df, width='stretch')
st.session_state['col_names_values'] = list(edited_col_names.iloc[0])

# Initialize or adjust table data
if 'table_data' not in st.session_state:
    st.session_state['table_data'] = pd.DataFrame(0.0, index=st.session_state['row_names_values'], columns=st.session_state['col_names_values'])
else:
    current_rows, current_cols = st.session_state['table_data'].shape
    if current_rows != num_rows or current_cols != num_cols:
        new_df = pd.DataFrame(0.0, index=st.session_state['row_names_values'], columns=st.session_state['col_names_values'])
        # Copy existing data if possible
        min_r = min(current_rows, num_rows)
        min_c = min(current_cols, num_cols)
        for i in range(min_r):
            for j in range(min_c):
                try:
                    new_df.iloc[i, j] = st.session_state['table_data'].iloc[i, j]
                except:
                    pass
        st.session_state['table_data'] = new_df

# Editable table (lookup table)
st.subheader("Table de lookup")
table_data = st.data_editor(st.session_state['table_data'], width='stretch')
st.session_state['table_data'] = table_data

# Slider for common x
selected_x = None
if 'mat_data' in st.session_state and 'sLap' in st.session_state['mat_data']:
    sLap = st.session_state['mat_data']['sLap'].flatten()
    min_x = float(sLap.min())
    max_x = float(sLap.max())
    selected_x = st.slider("Sélectionner l'abscisse commune", min_value=min_x, max_value=max_x, value=min_x, step=(max_x - min_x) / 100.0)
    st.session_state['selected_x'] = selected_x

# Plot
st.subheader("Visualisation")
if not table_data.empty:
    fig = px.imshow(table_data.values, text_auto=True, aspect="auto")
    st.plotly_chart(fig)
else:
    st.write("Aucune donnée à afficher")

# Signals plot
if 'mat_data' in st.session_state:
    mat_data = st.session_state['mat_data']
    if 'sLap' in mat_data:
        sLap = mat_data['sLap']
        fig_signals_slip = go.Figure()
        fig_signals_rTorque = go.Figure()
        for key, value in mat_data.items():
            if key != 'sLap' and 'slip' in key.lower():
                fig_signals_slip.add_trace(go.Scatter(x=sLap, y=value, mode='lines', name=key))
            if key != 'sLap' and key.lower().startswith('rtorque'):
                fig_signals_rTorque.add_trace(go.Scatter(x=sLap, y=value, mode='lines', name=key))
        st.subheader("Signaux temporels")
        if fig_signals_slip.data:
            st.plotly_chart(fig_signals_slip)
        if fig_signals_rTorque.data:
            st.plotly_chart(fig_signals_rTorque)
    else:
        st.write("Variable 'sLap' non trouvée dans le fichier MAT.")
else:
    st.write("Aucun fichier MAT chargé.")

# Button
if st.button("Lancer les calculs"):
    # Access table_data and uploaded_file here
    if 'uploaded_file' in st.session_state:
        st.write("Fichier :", st.session_state['uploaded_file'].name)
    st.write("Données de la table :", table_data.to_dict())
    st.write("Valeurs des noms de lignes :", st.session_state['row_names_values'])
    st.write("Valeurs des noms de colonnes :", st.session_state['col_names_values'])
    # Perform calculations here
    st.success("Calculs lancés !")