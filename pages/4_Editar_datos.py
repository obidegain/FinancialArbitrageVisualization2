import streamlit as st
import copy
import pandas as pd
from connect_with_bbdd import connect_to_bbdd, get_all_data_from_table, modify_specific_record_of_hisotricalprice, modify_specific_record_of_current_taxes


@st.cache_data(show_spinner=False)
def read_ddbb_historicalprice():
    conn = connect_to_bbdd()
    rows = get_all_data_from_table(conn, table='historicalprice')
    columns = ['date', 'price', 'ticker', 'tax', 'from_api', 'index']
    df = pd.DataFrame(rows, columns=columns)
    df['date'] = df['date'].str.replace(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', r'\2/\3/\1', regex=True)
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y').dt.date
    df.sort_values(by=['date',], inplace=True, ascending=False)
    return df


def get_modify_rows(df, df_modify):
    if len(list(df.compare(df_modify).index)) > 0:
        rows_to_modify = df_modify.loc[list(df.compare(df_modify).index)]
    else:
        rows_to_modify = pd.DataFrame()
    return rows_to_modify


def main():

    with st.spinner("Obteniendo datos..."):
        df = read_ddbb_historicalprice()
        df.set_index('index', inplace=True)
    st.success("¡Datos obtenidos exitosamente!")

    edited_df = st.data_editor(
        data=df,
        num_rows="dynamic",
        column_order=['index', 'date', 'ticker', 'tax', 'price', 'from_api'],
        disabled=['index', 'ticker', 'from_api']
    )

    if st.button("Ver celdas a modificar"):
        modify_df = edited_df.copy()
        rows_to_modify = get_modify_rows(df, modify_df)
        if len(rows_to_modify) > 0:
            st.session_state.rows_to_modify = rows_to_modify
        st.dataframe(rows_to_modify)

    if st.button("Aplicar cambios en base de datos"):
        if len(st.session_state.rows_to_modify) > 0:
            rows_to_modify = st.session_state.rows_to_modify
            with st.spinner("Actualizando datos..."):
                modify_specific_record_of_hisotricalprice(rows_to_modify)
            st.success("¡Datos actualizados exitosamente!")
            st.rerun()


if __name__ == "__main__":
    main()

