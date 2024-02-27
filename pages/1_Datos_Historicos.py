import streamlit as st
from strategy.strategy import Commodity
import streamlit as st
import pandas as pd
from connect_with_bbdd import connect_to_bbdd, get_all_data_from_table, modify_specific_record_of_hisotricalprice
from strategy.mapping_names import get_pretty_names

st.set_page_config(layout="wide")

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


@st.cache_data(show_spinner=False)
def read_ddbb_currenttaxes():
    conn = connect_to_bbdd()
    rows = get_all_data_from_table(conn, table='current_taxes')
    columns = ['commodity', 'market', 'current_tax', 'index']
    df = pd.DataFrame(rows, columns=columns)
    return df


def get_tickers():
    tickers = st.session_state.all_data['ticker'].unique()
    tickers_unique = set()
    for ticker in tickers:
        ticker_without_year = ticker[:-2]
        if "/" in ticker_without_year:
            tickers_unique.add(ticker_without_year)
    tickers_unique_list = list(tickers_unique)
    return tickers_unique_list


def get_modify_rows(df, df_modify):
    if len(list(df.compare(df_modify).index)) > 0:
        rows_to_modify = df_modify.iloc[list(df.compare(df_modify).index)]
    else:
        rows_to_modify = pd.DataFrame()
    return rows_to_modify


@st.cache_data
def get_commodity(ticker_selected, data_a, taxes):
    return Commodity(ticker_selected, data_a, taxes)


def get_df_filtered_by_ticker(df, ticker_selected):
    df_filtered = df[df['ticker'].str.contains(ticker_selected)].copy()
    df_filtered['date'] = pd.to_datetime(df_filtered['date'], format='%m/%d/%Y').dt.date
    return df_filtered


def main():
    if "all_data" not in st.session_state.keys():
        with st.spinner("Obteniendo datos..."):
            df = read_ddbb_historicalprice()
            st.session_state.all_data = df

            taxes = read_ddbb_currenttaxes()
            st.session_state.taxes = taxes

            tickers = get_tickers()
            st.session_state.tickers = tickers

        st.sidebar.success("¡Datos obtenidos exitosamente!")

    ticker_selected = st.sidebar.selectbox('Seleccione un commodity:', st.session_state.tickers)

    # Botones principales
    if st.sidebar.button("Visualizar Data"):

        with st.spinner("Obteniendo datos..."):
            st.session_state.ticker_selected = ticker_selected
            df = st.session_state.all_data
            st.session_state.df_filtered = get_df_filtered_by_ticker(df, ticker_selected)
        st.sidebar.success("¡Datos filtrados exitosamente!")

        with st.spinner("Formateando y calculando información extra..."):
            commodity_a = get_commodity(ticker_selected, st.session_state.df_filtered, st.session_state.taxes)
            st.session_state.commodity_a = commodity_a
        st.sidebar.success("¡Datos listos!")

    # Título de la aplicación
    if "commodity_a" not in st.session_state.keys():
        st.title(f'🌽 Datos históricos de {get_pretty_names(ticker_selected)}')

    else:
        st.title(f'🌽 Datos históricos de {get_pretty_names(st.session_state.ticker_selected)}')

        commodity_a = st.session_state.commodity_a
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                year = st.selectbox('Seleccione un año para calcular métricas:', commodity_a.data_to_plot['year_from_ticker'].unique())

        with st.container():
            main_measures = commodity_a.get_main_measures(year)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    f'Último precio del {main_measures.get("last_date")}:',
                    f"$ {main_measures.get('last_price'):.2f}",
                    delta=f"{main_measures.get('percent_change'):.1f} %",
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col2:
                st.metric(
                    'Máximo anual actual',
                    f"$ {main_measures.get('max_current_year'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col3:
                st.metric(
                    'Mínimo anual actual',
                    f"$ {main_measures.get('min_current_year'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

        with st.container():
            main_measures = commodity_a.get_main_measures(year)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    'Promedio histórico:',
                    f"$ {main_measures.get('hisotical_avg'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col2:
                st.metric(
                    'Promedio histórico para el mismo día:',
                    f"$ {main_measures.get('avg_price_for_last_date'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col3:
                st.metric(
                    'GAP Precio actual/Promedio histórico:',
                    f"{main_measures.get('gap'):.0f} %",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

        tab1, tab2, tab3 = st.tabs(["📈 Resumen", "🗃 Datos ticker", "👮‍♂️ Datos impuestos"])

        pivot_table = commodity_a.pivot_table
        fig = commodity_a.get_fig()

        tab1.plotly_chart(fig, theme="streamlit", use_container_width=True)
        tab1.dataframe(pivot_table)

        tab2.write("Datos Ticker:")
        tab2.dataframe(commodity_a.data_to_plot)

        tab3.write("Datos Retenciones:")
        tab3.dataframe(commodity_a.taxes)


if __name__ == "__main__":
    main()
