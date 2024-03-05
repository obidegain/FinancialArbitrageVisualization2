import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv('DBNAME')
user = os.getenv('USER_DB')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
port = os.getenv('PORT_DB')
sslmode = os.getenv('SSLMODE')


def connect_to_bbdd():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode=sslmode
        )
        print("¡Conexión exitosa!")
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)


def execute_psql_command(conn, command):
    """
    :param conn: it's a conection with psycopg2
    :param command: it's a sql_command, like a drop_table, add_table, modify_table, etc
    :return: nothing
    """
    try:
        cursor = conn.cursor()
        cursor.execute(command)
        conn.commit()
    except psycopg2.Error as e:
        print("Error al ejecutar el comando en la base de datos:", e)


def add_new_record_to_historical_prices(conn, data_to_insert):
    insert_query = '''
    INSERT INTO HistoricalPrice (date, price, ticker, tax, from_api)
    VALUES (%s, %s, %s, %s, %s);
    '''
    cursor = conn.cursor()
    cursor.execute(insert_query, data_to_insert)
    conn.commit()


def verify_conn_open(conn):
    if conn and not conn.closed:
        print("La conexión está abierta.")
        return True
    print("La conexión está cerrada o no se pudo establecer.")
    return False


def get_all_data_from_table(conn, table):
    select_query = f'SELECT * FROM {table};'
    cursor = conn.cursor()
    cursor.execute(select_query)
    rows = cursor.fetchall()
    return rows


def modify_specific_record_of_hisotricalprice(rows_to_modify):
    conn = connect_to_bbdd()
    print(rows_to_modify)
    rows_to_modify.reset_index(inplace=True)
    for i in range(len(rows_to_modify)):
        row = rows_to_modify.iloc[i]
        index, date, price, ticker, tax, from_api = list(row.values)
        index = int(index)
        query = """
            UPDATE historicalprice
            SET price = %s,
                tax = %s,
                from_api = %s
            WHERE index = %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (price, tax, from_api, index))
        conn.commit()
    conn.close()


def modify_specific_record_of_current_taxes(rows_to_modify):
    conn = connect_to_bbdd()
    rows_to_modify.reset_index(inplace=True)
    for i in range(len(rows_to_modify)):
        row = rows_to_modify.iloc[i]
        print(list(row.values))
        index, commodity, market, current_tax = list(row.values)
        index = int(index)
        query = """
            UPDATE current_taxes
            SET current_tax = %s
            WHERE index = %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (current_tax, index))
        conn.commit()
    conn.close()


def delete_all_records_of_specific_table(conn, table):
    select_query = f'DELETE FROM {table};'

    cursor = conn.cursor()
    cursor.execute(select_query)
    conn.commit()

    select_query = f'SELECT * FROM {table};'
    cursor = conn.cursor()
    cursor.execute(select_query)
    rows = cursor.fetchall()

    return rows


def get_files(path):
    try:
        files = os.listdir(path)
        return files
    except OSError as e:
        print(f"No se pudo acceder a la carpeta: {e}")
        return []


def upload_data_from_csv_to_historicalprice(conn, path='/home/obidegain/Workspaces/FinancialArbitrageVisualization2/data/archivos_finales'):
    files = get_files(path)
    cursor = conn.cursor()
    for file_name in files:
        if "_" in file_name:
            full_path = f'{path}/{file_name}'
            f = open(full_path, 'r')
            f.readline()
            print(file_name)
            if verify_conn_open(conn):
                print(f"Comenzando a cargar datos de {file_name}")
                cursor.copy_from(f, 'historicalprice', sep=',')
                conn.commit()
                print("Datos cargados exitosamente")
            print("")
            print(f'Cantidad de líneas: {len(get_all_data_from_table(conn, "historicalprice"))}')
            print("")


