import streamlit as st
import pandas as pd
import plotly.express as px

# Sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Sélectionner un fichier")
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        st.write("Fichier sélectionné :", uploaded_file.name)

# Main area
st.title("Carto Tuner")

# Inputs for table size
col1, col2 = st.columns(2)
with col1:
    num_rows = st.number_input("Nombre de lignes", min_value=1, value=5, step=1)
with col2:
    num_cols = st.number_input("Nombre de colonnes", min_value=1, value=5, step=1)

# Initialize or adjust table data
if 'table_data' not in st.session_state:
    st.session_state['table_data'] = pd.DataFrame(0.0, index=range(num_rows), columns=range(num_cols))
else:
    current_rows, current_cols = st.session_state['table_data'].shape
    if current_rows != num_rows or current_cols != num_cols:
        new_df = pd.DataFrame(0.0, index=range(num_rows), columns=range(num_cols))
        # Copy existing data if possible
        min_r = min(current_rows, num_rows)
        min_c = min(current_cols, num_cols)
        new_df.iloc[:min_r, :min_c] = st.session_state['table_data'].iloc[:min_r, :min_c]
        st.session_state['table_data'] = new_df

# Editable table (lookup table)
st.subheader("Table de lookup")
table_data = st.data_editor(st.session_state['table_data'], width='stretch')
st.session_state['table_data'] = table_data

# Plot
st.subheader("Visualisation")
if not table_data.empty:
    fig = px.imshow(table_data.values, text_auto=True, aspect="auto")
    st.plotly_chart(fig)
else:
    st.write("Aucune donnée à afficher")

# Button
if st.button("Lancer les calculs"):
    # Access table_data and uploaded_file here
    if 'uploaded_file' in st.session_state:
        st.write("Fichier :", st.session_state['uploaded_file'].name)
    st.write("Données de la table :", table_data.to_dict())
    # Perform calculations here
    st.success("Calculs lancés !")