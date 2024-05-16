import os
import pandas as pd
from datetime import datetime


def generate_all_csv_before_2023(folder):
    actual_folder = os.getcwd()
    #folder = "data/soja/mayo"
    data_folder = os.path.join(actual_folder, folder)

    if os.path.exists(data_folder):
        file_names = os.listdir(data_folder)
        all_file_name = [file for file in file_names if
                            os.path.isfile(os.path.join(data_folder, file))]

        COLUMNS_NAME = ['date', 'price', 'ticker', 'tax', 'from_api', 'index']
        df = pd.DataFrame(columns=COLUMNS_NAME)
        for file_name in all_file_name:
            try:
                full_path = f'{data_folder}/{file_name}'
                print(full_path)
                commodity, market, month_year = file_name.split(".csv")[0].split("-")
                position = f'{commodity}.{market}/{month_year}'
                df2 = get_data(full_path, position)
                frames = [df, df2]
                df = pd.concat(frames)
            except:
                print("error")
        df['tax'] = df.apply(apply_tax, axis=1)
        full_path_file = "/home/obidegain/Workspaces/FinancialArbitrageVisualization2/data/archivos_finales/"
        csv_file_name = f'{commodity}-{market}-{month_year[:-2]}.csv'
        df.to_csv(f'{full_path_file}{csv_file_name}', index=False)
    else:
        print("La carpeta 'data' no existe.")
    print(f'Proceso finalizado')
    print(f'Se creo el archivo: {csv_file_name}')


def generate_all_csv_after_2024():
    actual_folder = os.getcwd()
    #folder = "data/soja/mayo"
    data_folder = os.path.join(actual_folder, "data/2024")

    if os.path.exists(data_folder):
        file_names = os.listdir(data_folder)
        all_file_name = [file for file in file_names if
                            os.path.isfile(os.path.join(data_folder, file))]

        COLUMNS_NAME = ['date', 'price', 'ticker', 'tax', 'from_api', 'index']
        df = pd.DataFrame(columns=COLUMNS_NAME)
        for file_name in all_file_name:
            try:
                full_path = f'{data_folder}/{file_name}'
                print(full_path)
                commodity, market, month_year = file_name.split(".csv")[0].split("-")
                position = f'{commodity}.{market}/{month_year}'
                df2 = get_data_2024(full_path, position)
                frames = [df, df2]
                df = pd.concat(frames)
            except:
                print("error")

        df['tax'] = df.apply(apply_tax, axis=1)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.strftime('%d/%m/%Y')
        full_path_file = "/home/obidegain/Workspaces/FinancialArbitrageVisualization2/data/archivos_finales/"
        csv_file_name = f'2024.csv'
        df.to_csv(f'{full_path_file}{csv_file_name}', index=False)
    else:
        print("La carpeta 'data' no existe.")
    print(f'Proceso finalizado')
    print(f'Se creo el archivo: {csv_file_name}')


def get_taxes():
    full_path = "/home/obidegain/Workspaces/FinancialArbitrageVisualization2/data/retenciones.csv"
    taxes_df = pd.read_csv(full_path)
    return taxes_df


def get_data_2024(full_path, position):
    df = pd.read_csv(full_path)
    df['DECIMAL'] = df['DECIMAL'] / 1000000
    df['PRICE'] = df['TRADES'] + df['DECIMAL']
    df_filtered = df.loc[:, ['TIPO CONTRATO', 'FECHA', 'PRICE']].copy()
    df_filtered.rename(columns={"FECHA": "date", "PRICE": "price", "TIPO CONTRATO": "ticker"}, inplace=True)

    return df_filtered


def get_data(full_path, position):
    df = pd.read_csv(full_path)
    df_filtered = df.loc[:, ['Fecha', 'Cierre']].copy()
    df_filtered['ticker'] = position
    df_filtered.rename(columns={"Fecha": "date", "Cierre": "price", "ticker": "ticker"}, inplace=True)

    return df_filtered


def apply_tax(row):
    taxes = get_taxes()
    ticker = row['ticker']
    commodity, market = ticker.split("/")[0].split(".")

    format = "%d-%m-%Y"
    format_tax = "%d-%m-%Y"
    row['date'] = row['date'].replace("/", "-")
    row['date'] = datetime.strptime(row['date'], format)
    taxes['from'] = pd.to_datetime(taxes['from'], format=format_tax)
    taxes['to'] = pd.to_datetime(taxes['to'], format=format_tax)

    filtered_taxes = taxes[(taxes['market'] == market) & (taxes['commodity'] == commodity)]
    relevant_tax = filtered_taxes.loc[
        (filtered_taxes['from'] <= row['date']) & (row['date'] <= filtered_taxes['to']), 'tax']
    if not relevant_tax.empty:
        return relevant_tax.iloc[0]
    return 0


def generate_all_csv_from_cbot():
    actual_folder = os.getcwd()
    #folder = "data/soja/mayo"
    data_folder = os.path.join(actual_folder, "data/cbot")
    if os.path.exists(data_folder):
        # Lista de nombres de archivos en la carpeta "tickers"
        file_names = os.listdir(data_folder)
        all_file_name = [file for file in file_names if
                            os.path.isfile(os.path.join(data_folder, file))]


        COLUMNS_NAME = ['date', 'price', 'ticker', 'tax', 'from_api', 'index']
        df = pd.DataFrame(columns=COLUMNS_NAME)

        for file_name in all_file_name:
            try:
                full_path = f'{data_folder}/{file_name}'
                print(full_path)
                commodity, extra_info = file_name.split(".csv")[0].split(".")
                market, month = extra_info.split("_")
                position = f'{commodity}.{market}/{month}'
                df2 = get_data_2024_cbot(full_path, commodity)
                frames = [df, df2]
                df = pd.concat(frames)
            except Exception as e:
                print(e)
        full_path_file = "/home/obidegain/Workspaces/FinancialArbitrageVisualization2/data/archivos_finales/"
        csv_file_name = f'cbot.csv'
        df.to_csv(f'{full_path_file}{csv_file_name}', index=False)


def get_data_2024_cbot(full_path, commodity):
    from decimal import Decimal
    df = pd.read_csv(full_path)
    df.rename(columns={"ticket": "ticker"}, inplace=True)
    if commodity == "CRN":
        df['tax'] = Decimal(0.393685)
    elif commodity == "SOY":
        df['tax'] = Decimal(0.367437)
    return df
