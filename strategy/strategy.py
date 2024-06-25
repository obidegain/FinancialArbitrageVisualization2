import pandas as pd
from datetime import datetime
from strategy.mapping_names import get_pretty_names
import plotly.express as px

watermark_text = "@MarielaBrandolin"

factors = {
    'SOJ': 8,
    'MAI': 10,
    'TRI': 13
}


def add_one_year(row):
    year = int(row) + 1
    return str(year)


class Commodity:
    def __init__(self, name, data, taxes):
        self.name = name
        self.taxes = taxes
        self.pretty_name = get_pretty_names(name)
        self.market = self.name.split('.')[1].split('/')[0]
        self.commodity = self.name.split('.')[0]

        self.data = data.copy()

        self.data_to_plot = self.apply_format()
        self.pivot_table = self.pivot_table_creator()

    def _get_reference_date_to_graph(self, data):
        # Eliminar 29 de febrero
        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        condition = ~((data['date'].dt.month == 2) & (data['date'].dt.day == 29))
        data = data[condition]
        data['date'] = data['date'].dt.strftime('%d/%m/%Y')

        # Para poder graficar, necesitamos tener data solo de los últimos dos años
        data = data[data['year_from_ticker'] - data['year'] < 2]

        # Recorremos por cada ticker, que se tradean desde el año anterior por ejemplo SOJA JULIO 2018,
        # se comienza a tradear en agosto del 2017 hasta julio del 2018. Por lo tanto, agarramos los
        # tickets nos fijamos que tenga trades en 1 año o en 2 y al menor año le aplicamos el año 2012
        # y al mayor el año 2013. Asi todos los tickers nos quedan en la misma referencia temporal para graficar
        for ticker in data['ticker'].unique():
            data.loc[data['ticker'] == ticker, 'reference_date'] = 2017 - (
                        data.loc[data['ticker'] == ticker, 'year_from_ticker'] - data.loc[
                    data['ticker'] == ticker, 'year'])

        # Creamos una nueva columna con la nueva fecha con los años 2016 y 2017
        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        data['reference_date'] = pd.to_datetime(data['reference_date'], format='%Y')

        data['date_to_graph'] = ""

        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        data['year'] = data['reference_date'].dt.year
        data['week'] = data['date'].dt.strftime('%U').astype(int) + 1
        data['day_of_week'] = data['date'].dt.dayofweek + 1
        # Hay que trabajar con el día de la semana y el número de la semana porque si utilizas el
        # día extacto, corres el riesgo de trasladarte de año y que un martes sea un domingo, en cambio
        # de esta manera, comparas el martes de la semana núermo 16 contra el martes de la semana 16 aunque
        # uno sea el 10/04 y el otro sea el 15/4 (es un ejemplo)

        data = data[data['week'] != 54]
        data = data[data['day_of_week'] != 7]
        data['date_to_graph'] = pd.to_datetime(
            data['year'].astype(str) + '-W' + data['week'].astype(str) + '-' + data['day_of_week'].astype(str),
            format='%Y-W%U-%w'
        )

        # Formateamos las columnas
        data['date_to_graph'] = pd.to_datetime(data['date_to_graph'], format='%d/%m/%Y').dt.date
        data['date'] = data['date'].dt.date
        data['reference_date'] = data['reference_date'].dt.date

        return data

    def apply_format(self):
        data = self.data
        taxes = self.taxes

        # Convertir la columna 'Fecha' en objeto de fecha y hora
        data['date'] = pd.to_datetime(data['date'])

        # Extraer solo la parte de la fecha (eliminar la hora)
        data['year'] = data['date'].dt.year
        data['date'] = data['date'].dt.date

        data['price'] = data['price'].astype(float)
        data['tax'] = data['tax'].astype(float)

        print(f'commodity strategy: {self.commodity}')
        print(f'market strategy: {self.market}')

        if self.market == 'CME':
            data['price_without_tax'] = data['price'] * data['tax']
        else:
            current_tax = taxes[(taxes['commodity'] == self.commodity) & (taxes['market'] == self.market)]['current_tax'].values[0]
            factor = factors.get(self.commodity)
            data['price_without_tax'] = data['price'] + ((data['price'] + factor) / (1 - data['tax'])) * (data['tax'] - float(current_tax))


        # Extraemos el año del ticker
        data['year_from_ticker'] = data['ticker'].str[-2:]
        data['year_from_ticker'] = pd.to_datetime(data['year_from_ticker'], format='%y')
        data['year_from_ticker'] = data['year_from_ticker'].dt.year

        data = self._get_reference_date_to_graph(data)

        # Lista con el nuevo orden de las columnas
        new_order = ['ticker',
                     'year_from_ticker',
                     'date',
                     'year',
                     'reference_date',
                     'date_to_graph',
                     'price',
                     'tax',
                     'price_without_tax',
                     ]
        # Reordenar las columnas utilizando reindex
        data = data.reindex(columns=new_order)
        return data

    def pivot_table_creator(self):
        data = self.data_to_plot
        pivot_df = data.pivot_table(
            index='date_to_graph',
            columns='year_from_ticker',
            values='price',
            aggfunc='mean'
        )

        df = pivot_df.ffill(limit=5)

        # Agregar la columna "promedio" al final
        df['promedio'] = df.mean(axis=1)

        return df

    def get_fig(self):
        pivot_table = self.pivot_table
        fig = px.line(
            pivot_table,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(
            title_text='Precios históricos',
            title_x=0.4)
        fig.update_yaxes(
            title_text="Precio",
            range=[pivot_table.values.min(), pivot_table.values.max()]
        )

        # Asumiendo que las fechas están en el índice del DataFrame
        dates = pd.to_datetime(pivot_table.index)  # Convertir el índice a datetime si no lo está

        # Extraer los meses
        months = dates.strftime('%b')  # Abreviatura de mes, por ejemplo 'Jan', 'Feb', etc.

        # Asegúrate de que etiquetas_personalizadas tenga el mismo número de elementos que los ticks que quieras mostrar.
        tick_positions = dates[::30]  # Muestra un tick por cada 30 días, ajusta según sea necesario
        tick_text = months[::30]  # Etiquetas correspondientes a los ticks seleccionados

        fig.update_xaxes(
            title_text="",
            showticklabels=True,
            tickvals=tick_positions,
            ticktext=tick_text,
            rangeslider=dict(
                visible=True,
                bgcolor='rgb(242, 244, 244)',
                thickness=0.05
            )
        )
        # Personalizar la serie "promedio" como línea punteada y negra
        fig.update_traces(
            selector=dict(name='promedio'),  # Nombre de la serie
            line=dict(dash='dot', color='black')  # Línea punteada y negra
        )

        fig.layout.annotations = [
            dict(
                name="mbrandolin watermark",
                text=watermark_text,
                textangle=0,
                opacity=0.1,
                font=dict(color="black", size=50),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ]

        trace_count = len(fig.data)
        if trace_count > 1:
            fig.data[trace_count - 3].update(line=dict(color='black', width=3))
            fig.data[trace_count - 2].update(line=dict(color='crimson', width=3))

        return fig.update_layout(height=600, width=800)

    def get_main_measures(self, year):
        pivot_table = self.pivot_table
        data_to_plot = self.data_to_plot
        data = pivot_table[year]
        hisotical_avg = pivot_table['promedio'].mean()
        max_current_year = data.sort_index(ascending=True).max()
        min_current_year = data.sort_index(ascending=True).min()

        data_from_plot = data_to_plot[data_to_plot['year_from_ticker'] == year]
        last_date = data_from_plot.sort_values(by='date', ascending=True).iloc[-1]['date']
        last_price = data_from_plot.sort_values(by='date', ascending=True).iloc[-1]['price']
        if len(data_from_plot) >= 2:
            one_day_ago_of_last_price = data_from_plot.sort_values(by='date', ascending=True).iloc[-2]['price']
        else:
            one_day_ago_of_last_price = last_price
        percent_change = ((last_price - one_day_ago_of_last_price) / one_day_ago_of_last_price) * 100

        last_date_with_reference_to_graph = data_from_plot.sort_values(by='date', ascending=True).iloc[-1]['date_to_graph']
        avg_price_for_last_date = pivot_table.loc[last_date_with_reference_to_graph]['promedio']
        gap = ((last_price - avg_price_for_last_date) / avg_price_for_last_date) * 100
        main_measures = {
            'hisotical_avg': hisotical_avg,
            'max_current_year': max_current_year,
            'min_current_year': min_current_year,
            'last_date': last_date,
            'last_price': last_price,
            'percent_change': percent_change,
            'avg_price_for_last_date': avg_price_for_last_date,
            'gap': gap
        }
        return main_measures


class CommodityAnalyzer:
    def __init__(self, commodity_a, commodity_b):
        self.commodity_a = Commodity(commodity_a['name'], commodity_a['data'], commodity_a['taxes'])
        self.commodity_b = Commodity(commodity_b['name'], commodity_b['data'], commodity_b['taxes'])
        self.combined_price_ratio = self.calculate_ratio_per_expiration_date()
        self.data_to_plot = self._get_reference_date_to_graph(combined_price_ratio=self.combined_price_ratio)
        self.pivot_table_relative, self.pivot_table_nominal = self.pivot_table_creator_strategy(data_to_plot=self.data_to_plot)


    def calculate_ratio_per_expiration_date(self):
        data_a = self.commodity_a.data
        data_b = self.commodity_b.data

        # Agregar una columna para el año en ambos dataframes
        data_a['year_from_ticker'] = data_a['ticker'].str[-2:]
        data_b['year_from_ticker'] = data_b['ticker'].str[-2:]
        #data_b['year_from_ticker'] = data_b['ticker'].str[-2:].apply(add_one_year)

        merged_df = pd.merge(data_a, data_b, on=['date', 'year_from_ticker'], how='inner')

        merged_df['ratio_relative'] = merged_df['price_without_tax_x'] / merged_df['price_without_tax_y']
        merged_df['ratio_nominal'] = merged_df['price_without_tax_x'] - merged_df['price_without_tax_y']

        new_order = [
            'date',
            'year_from_ticker',
            'ticker_x',
            'price_without_tax_x',
            'tax_x',
            'price_x',
            'ticker_y',
            'price_without_tax_y',
            'tax_y',
            'price_y',
            'ratio_relative',
            'ratio_nominal'
        ]

        merged_df = merged_df[new_order]

        merged_df['year_from_date'] = merged_df['date'].dt.year
        merged_df['date'] = merged_df['date'].dt.date

        merged_df['year_from_ticker'] = pd.to_datetime(merged_df['year_from_ticker'], format='%y')
        merged_df['year_from_ticker'] = merged_df['year_from_ticker'].dt.year

        return merged_df

    def _get_reference_date_to_graph(self, combined_price_ratio):
        data = combined_price_ratio

        # Eliminar 29 de febrero
        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        condition = ~((data['date'].dt.month == 2) & (data['date'].dt.day == 29))
        data = data[condition]
        data['date'] = data['date'].dt.strftime('%d/%m/%Y')

        # Para poder graficar, necesitamos tener data solo de los últimos dos años por cada posición
        data = data[data['year_from_ticker'] - data['year_from_date'] < 2]

        # Recorremos por cada ticker, que se tradean desde el año anterior por ejemplo SOJA JULIO 2018,
        # se comienza a tradear en agosto del 2017 hasta julio del 2018. Por lo tanto, agarramos los
        # tickers nos fijamos que tenga trades en 1 año o en 2 y al menor año le aplicamos el año 2012
        # y al mayor el año 2013. Asi todos los tickers nos quedan en la misma referencia temporal para graficar
        for ticker in data['ticker_x'].unique():
            data.loc[data['ticker_x'] == ticker, 'reference_date'] = 2017 - (data.loc[data['ticker_x'] == ticker, 'year_from_ticker'] - data.loc[data['ticker_x'] == ticker, 'year_from_date'])

        # Creamos una nueva columna con la nueva fecha con los años 2012 y 2013
        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        data['reference_date'] = pd.to_datetime(data['reference_date'], format='%Y')

        day_month = data['date'].dt.strftime('%d/%m')
        year = data['reference_date'].dt.year

        data['date_to_graph'] = day_month + '/' + year.astype(str)
        data['date_to_graph2'] = ""

        data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
        data['year'] = data['reference_date'].dt.year
        data['week'] = data['date'].dt.strftime('%U').astype(int) + 1
        data['day_of_week'] = data['date'].dt.dayofweek + 1
        # Hay que trabajar con el día de la semana y el número de la semana porque si utilizas el
        # día extacto, corres el riesgo de trasladarte de año y que un martes sea un domingo, en cambio
        # de esta manera, comparas el martes de la semana núermo 16 contra el martes de la semana 16 aunque
        # uno sea el 10/04 y el otro sea el 15/4 (es un ejemplo)
        data = data[data['week'] != 54]
        data['date_to_graph2'] = pd.to_datetime(
            data['year'].astype(str) + '-W' + data['week'].astype(str) + '-' + data['day_of_week'].astype(str),
            format='%Y-W%U-%w'
        )

        # Formateamos las columnas
        data['date_to_graph'] = pd.to_datetime(data['date_to_graph'], format='%d/%m/%Y').dt.date
        data['date_to_graph2'] = pd.to_datetime(data['date_to_graph2'], format='%d/%m/%Y').dt.date
        data['date'] = data['date'].dt.date
        data['reference_date'] = data['reference_date'].dt.date

        new_order = [
            'date_to_graph',
            'date_to_graph2',
            'date',
            'year_from_ticker',
            'year_from_date',
            'ticker_x',
            'price_without_tax_x',
            'tax_x',
            'price_x',
            'ticker_y',
            'price_without_tax_y',
            'tax_y',
            'price_y',
            'ratio_relative',
            'ratio_nominal'
        ]
        data = data.reindex(columns=new_order)

        return data

    def pivot_table_creator_strategy(self, data_to_plot):
        data_to_plot = data_to_plot

        pivot_df_relative = data_to_plot.pivot_table(
            index='date_to_graph',
            columns='year_from_ticker',
            values='ratio_relative',
            aggfunc='mean'
        )

        pivot_df_nominal = data_to_plot.pivot_table(
            index='date_to_graph',
            columns='year_from_ticker',
            values='ratio_nominal',
            aggfunc='mean'
        )

        df_relative = pivot_df_relative.fillna(method='ffill', limit=5)
        df_nominal = pivot_df_nominal.fillna(method='ffill', limit=5)

        # Agregar la columna "promedio" al final
        df_relative['promedio'] = df_relative.mean(axis=1)
        df_nominal['promedio'] = df_nominal.mean(axis=1)

        return df_relative, df_nominal

    def get_fig_strategy(self, relative_or_nominal="Porcentual"):
        if relative_or_nominal == 'Porcentual':
            data_to_pivot = self.pivot_table_relative
        else:
            data_to_pivot = self.pivot_table_nominal

        fig = px.line(
            data_to_pivot,
            title=f'Ratio {self.commodity_a.pretty_name} / {self.commodity_b.pretty_name}',
        )
        fig.update_yaxes(
            range=[data_to_pivot.values.min(), data_to_pivot.values.max()]
        )
        # Asumiendo que las fechas están en el índice del DataFrame
        dates = pd.to_datetime(data_to_pivot.index)  # Convertir el índice a datetime si no lo está

        # Extraer los meses
        months = dates.strftime('%b')  # Abreviatura de mes, por ejemplo 'Jan', 'Feb', etc.

        # Asegúrate de que etiquetas_personalizadas tenga el mismo número de elementos que los ticks que quieras mostrar.
        tick_positions = dates[::30]  # Muestra un tick por cada 30 días, ajusta según sea necesario
        tick_text = months[::30]  # Etiquetas correspondientes a los ticks seleccionados

        fig.update_xaxes(
            title_text="",
            showticklabels=True,
            tickvals=tick_positions,
            ticktext=tick_text,
            rangeslider=dict(
                visible=True,
                bgcolor='rgb(242, 244, 244)',
                thickness=0.05
            )
        )
        # Personalizar la serie "promedio" como línea punteada y negra
        fig.update_traces(
            selector=dict(name='promedio'),  # Nombre de la serie
            line=dict(dash='dot', color='black')  # Línea punteada y negra
        )
        fig.update_layout(height=600, width=800)

        fig.layout.annotations = [
            dict(
                name="mbrandolin watermark",
                text=watermark_text,
                textangle=0,
                opacity=0.1,
                font=dict(color="black", size=100),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ]

        trace_count = len(fig.data)
        if trace_count > 1:
            fig.data[trace_count - 3].update(line=dict(color='black', width=3))
            fig.data[trace_count - 2].update(line=dict(color='crimson', width=3))

        return fig

    def get_main_measures(self, year, relative_or_nominal='Porcentual'):
        if relative_or_nominal == 'Porcentual':
            pivot_table = self.pivot_table_relative
        else:
            pivot_table = self.pivot_table_nominal

        data_to_plot = self.data_to_plot.sort_values(by='date', ascending=False)
        relative_or_nominal_dict = {
            'Porcentual': 'relative',
            'Absoluto': 'nominal'
        }
        type_ratio = f'ratio_{relative_or_nominal_dict.get(relative_or_nominal)}'

        data = pivot_table[year]
        hisotical_avg = pivot_table['promedio'].mean()
        max_current_year = data.sort_index(ascending=True).max()
        min_current_year = data.sort_index(ascending=True).min()

        data_from_plot = data_to_plot[data_to_plot['year_from_ticker'] == year]
        last_date = data_from_plot.sort_values(by='date', ascending=True).iloc[-1]['date']
        last_price = data_from_plot.sort_values(by='date', ascending=True).iloc[-1][type_ratio]
        if len(data_from_plot) >= 2:
            one_day_ago_of_last_price = data_from_plot.sort_values(by='date', ascending=True).iloc[-2][type_ratio]
        else:
            one_day_ago_of_last_price = last_price
        percent_change = ((last_price - one_day_ago_of_last_price) / one_day_ago_of_last_price) * 100

        last_date_with_reference_to_graph = data_from_plot.sort_values(by='date', ascending=True).iloc[-1]['date_to_graph']
        avg_price_for_last_date = pivot_table.loc[last_date_with_reference_to_graph]['promedio']
        gap = ((last_price - avg_price_for_last_date) / avg_price_for_last_date) * 100

        main_measures = {
            'hisotical_avg': hisotical_avg,
            'max_current_year': max_current_year,
            'min_current_year': min_current_year,
            'last_date': last_date,
            'last_price': last_price,
            'percent_change': percent_change,
            'avg_price_for_last_date': avg_price_for_last_date,
            'gap': gap
        }
        return main_measures
