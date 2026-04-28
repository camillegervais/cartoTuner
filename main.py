import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.io import loadmat
from data_input_processing import *
from calc_processing import calculate_lookup_results

st.set_page_config(layout="wide")


def load_sidebar():
    with st.sidebar:
        uploaded_file = st.file_uploader("Sélectionner un fichier")
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file
            mat_data = loadmat(uploaded_file)
            mat_data = clean_input_data(mat_data)
            st.session_state['mat_data'] = mat_data
            st.write("Fichier chargé :", uploaded_file.name)
            st.write("Variables disponibles :", list(mat_data.keys()))


def get_table_size_inputs():
    col1, col2 = st.columns(2)
    with col1:
        num_rows = st.number_input("Nombre de lignes", min_value=1, value=5, step=1)
    with col2:
        num_cols = st.number_input("Nombre de colonnes", min_value=1, value=5, step=1)
    return num_rows, num_cols


def ensure_axis_values_length(num_rows, num_cols):
    if 'row_names_values' not in st.session_state or len(st.session_state['row_names_values']) != num_rows:
        current = st.session_state.get('row_names_values', [])
        if len(current) < num_rows:
            start = max(current) + 1 if current else 0
            current += [start + i for i in range(num_rows - len(current))]
        else:
            current = current[:num_rows]
        st.session_state['row_names_values'] = current

    if 'col_names_values' not in st.session_state or len(st.session_state['col_names_values']) != num_cols:
        current = st.session_state.get('col_names_values', [])
        if len(current) < num_cols:
            start = max(current) + 1 if current else 0
            current += [start + i for i in range(num_cols - len(current))]
        else:
            current = current[:num_cols]
        st.session_state['col_names_values'] = current


def ensure_unique_values(values):
    if len(set(values)) == len(values):
        return values

    unique_values = []
    seen = set()
    for v in values:
        while v in seen:
            v += 0.001
        unique_values.append(v)
        seen.add(v)
    return unique_values


def edit_axis_tables(num_rows, num_cols):
    st.subheader("Valeurs des noms de lignes")
    row_names_df = pd.DataFrame([st.session_state['row_names_values']], columns=[f'Row {i+1}' for i in range(num_rows)])
    edited_row_names = st.data_editor(row_names_df, width='stretch')
    st.session_state['row_names_values'] = list(edited_row_names.iloc[0])
    st.session_state['row_names_values'] = ensure_unique_values(st.session_state['row_names_values'])

    st.subheader("Valeurs des noms de colonnes")
    col_names_df = pd.DataFrame([st.session_state['col_names_values']], columns=[f'Col {i+1}' for i in range(num_cols)])
    edited_col_names = st.data_editor(col_names_df, width='stretch')
    st.session_state['col_names_values'] = list(edited_col_names.iloc[0])
    st.session_state['col_names_values'] = ensure_unique_values(st.session_state['col_names_values'])


def init_lookup_table():
    if 'table_data' not in st.session_state or not isinstance(st.session_state['table_data'], pd.DataFrame):
        st.session_state['table_data'] = pd.DataFrame(
            0.0,
            index=st.session_state['row_names_values'],
            columns=st.session_state['col_names_values']
        )
        return

    if isinstance(st.session_state['table_data'], dict):
        st.session_state['table_data'] = pd.DataFrame(st.session_state['table_data'])

    new_df = st.session_state['table_data'].reindex(
        index=st.session_state['row_names_values'],
        columns=st.session_state['col_names_values'],
        fill_value=0.0
    )
    if not st.session_state['table_data'].equals(new_df):
        st.session_state['table_data'] = new_df


def render_lookup_editor():
    st.subheader("Table de lookup")
    table_data = st.data_editor(
        st.session_state['table_data'],
        key="data_editor_key",
        width='stretch'
    )
    st.session_state['table_data'] = table_data
    return table_data


def render_heatmap(table_data):
    st.subheader("Visualisation")
    if not table_data.empty:
        fig = px.imshow(table_data.values, text_auto=True, aspect="auto")
        st.plotly_chart(fig)
    else:
        st.write("Aucune donnée à afficher")


def render_signals():
    if 'mat_data' not in st.session_state:
        st.write("Aucun fichier MAT chargé.")
        return

    mat_data = st.session_state['mat_data']
    if 'sLap' not in mat_data:
        st.write("Variable 'sLap' non trouvée dans le fichier MAT.")
        return

    sLap = mat_data['sLap']
    fig_signals_slip = go.Figure()
    fig_signals_rTorque = go.Figure()
    for key, value in mat_data.items():
        if key == 'sLap':
            continue
        if 'slip' in key.lower():
            fig_signals_slip.add_trace(go.Scatter(x=sLap, y=value, mode='lines', name=key))
        if key.lower().startswith('rtorque'):
            fig_signals_rTorque.add_trace(go.Scatter(x=sLap, y=value, mode='lines', name=key))

    st.subheader("Signaux temporels")
    if fig_signals_slip.data:
        st.plotly_chart(fig_signals_slip)
    if fig_signals_rTorque.data:
        st.plotly_chart(fig_signals_rTorque)


def render_footer(table_data):
    if st.button("Lancer les calculs"):
        if 'uploaded_file' in st.session_state:
            st.write("Fichier :", st.session_state['uploaded_file'].name)

        results = calculate_lookup_results(
            mat_data=st.session_state.get('mat_data'),
            lookup_table=table_data,
            row_values=st.session_state['row_names_values'],
            col_values=st.session_state['col_names_values']
        )

        st.write("Résultats de calcul :")
        st.json(results)
        st.success("Calculs lancés !")


def main():
    st.title("Carto Tuner")
    load_sidebar()
    num_rows, num_cols = get_table_size_inputs()
    ensure_axis_values_length(num_rows, num_cols)
    edit_axis_tables(num_rows, num_cols)
    init_lookup_table()
    table_data = render_lookup_editor()
    render_heatmap(table_data)
    render_signals()
    render_footer(table_data)


if __name__ == '__main__':
    main()