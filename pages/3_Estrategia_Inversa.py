import streamlit as st
from strategy.strategy_inverse import CommodityAnalyzerInverse
import streamlit as st
import pandas as pd
from connect_with_bbdd import connect_to_bbdd, get_all_data_from_table
from strategy.mapping_names import get_pretty_names, valid_tickers

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
        if "/" in ticker_without_year and ticker_without_year in valid_tickers:
            tickers_unique.add(ticker_without_year)
    tickers_unique_list = sorted(list(tickers_unique), reverse=True)
    return tickers_unique_list


@st.cache_data
def get_commodity_analyzer(commodity_a, commodity_b):
    return CommodityAnalyzerInverse(commodity_a, commodity_b)


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


    tickers = get_tickers()

    ticker_selected_a = st.sidebar.selectbox('Seleccione el primer commodity', tickers)
    ticker_selected_b = st.sidebar.selectbox('Seleccione el segundo commodity', tickers)

    # Botones principales
    if st.sidebar.button("Crear estrategia"):
        with st.spinner("Obteniendo datos..."):
            st.session_state.ticker_selected_a = ticker_selected_a
            st.session_state.ticker_selected_b = ticker_selected_b
            df = st.session_state.all_data
            st.session_state.df_filtered_a = get_df_filtered_by_ticker(df, ticker_selected_a)
            st.session_state.df_filtered_b = get_df_filtered_by_ticker(df, ticker_selected_b)
        st.sidebar.success("¡Datos filtrados exitosamente!")

        with st.spinner("Formateando y calculando información extra..."):
            commodity_a = {
                'name': ticker_selected_a,
                'data': st.session_state.df_filtered_a,
                'taxes': st.session_state.taxes
            }
            commodity_b = {
                'name': ticker_selected_b,
                'data': st.session_state.df_filtered_b,
                'taxes': st.session_state.taxes
            }
            strategy = get_commodity_analyzer(commodity_a, commodity_b)
            st.session_state.strategy = strategy

        st.sidebar.success("¡Datos listos!")

    # Título de la aplicación
    if "ticker_selected_a" not in st.session_state.keys():
        st.title(f"📈 Estrategia {get_pretty_names(ticker_selected_a)} / {get_pretty_names(ticker_selected_b)}")

    else:
        st.title(f"📈 Estrategia {get_pretty_names(st.session_state.ticker_selected_a)} / {get_pretty_names(st.session_state.ticker_selected_b)}")
        strategy = st.session_state.strategy

        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                years = sorted(strategy.data_to_plot['year_from_ticker'].unique().tolist(), reverse=True)
                year = st.selectbox('Seleccione un año para calcular métricas:', years)
            with col5:
                relative_or_nominal = st.radio(
                    "¿En que formato te gustaría ver los datos?",
                    ["Porcentual", "Absoluto"],
                    horizontal=True,
                )

                main_measures = strategy.get_main_measures(year, relative_or_nominal=relative_or_nominal)
                fig = strategy.get_fig_strategy(relative_or_nominal=relative_or_nominal)
                if relative_or_nominal == "Porcentual":
                    pivot_table = strategy.pivot_table_relative
                elif relative_or_nominal == "Absoluto":
                    pivot_table = strategy.pivot_table_nominal

        with st.container():

            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            with col2:
                st.metric(
                    f'Ratio para el {main_measures.get("last_date")}:',
                    f"{main_measures.get('last_price'):.2f}",
                    delta=f"{main_measures.get('percent_change'):.1f} %",
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col4:
                st.metric(
                    'Máximo anual actual',
                    f"{main_measures.get('max_current_year'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col6:
                st.metric(
                    'Mínimo anual actual',
                    f"{main_measures.get('min_current_year'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

        with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            with col2:
                st.metric(
                    'Promedio histórico:',
                    f"{main_measures.get('hisotical_avg'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col4:
                st.metric(
                    'Promedio histórico para el mismo día:',
                    f"{main_measures.get('avg_price_for_last_date'):.2f}",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

            with col6:
                st.metric(
                    'GAP Precio actual/Promedio histórico:',
                    f"{main_measures.get('gap'):.0f} %",
                    delta=None,
                    delta_color="normal",
                    help=None,
                    label_visibility="visible"
                )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📈 Resumen",
                f"🗃 Datos {strategy.commodity_a.pretty_name}",
                f"🗃 Datos {strategy.commodity_b.pretty_name}",
                "👮‍♂️ Datos impuestos"
            ]
        )

        tab1.plotly_chart(fig, theme="streamlit", use_container_width=True)
        tab1.dataframe(pivot_table)

        tab2.write("Gráfico:")
        fig_a = strategy.commodity_a.get_fig()
        tab2.plotly_chart(fig_a, theme="streamlit", use_container_width=True)
        tab2.write("Pivot Table:")
        pivot_table_a = strategy.commodity_a.pivot_table
        tab2.dataframe(pivot_table_a)

        tab3.write("Gráfico:")
        fig_b = strategy.commodity_b.get_fig()
        tab3.plotly_chart(fig_b, theme="streamlit", use_container_width=True)
        tab3.write("Pivot Table:")
        pivot_table_b = strategy.commodity_b.pivot_table
        tab3.dataframe(pivot_table_b)

        tab4.write("Datos Retenciones:")
        tab4.dataframe(strategy.commodity_b.taxes)


if __name__ == "__main__":
    main()
