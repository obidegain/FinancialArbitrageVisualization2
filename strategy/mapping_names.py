mapping_names = {
    "ROS": "matba",
    "CME": "cbot",
    "SOJ": "soja",
    "SOY": "soja",
    "CRN": "maiz",
    "MAI": "maiz",
    "TRI": "trigo",
    "ENE": "enero",
    "FEB": "febrero",
    "MAR": "marzo",
    "MAY": "mayo",
    "JUN": "junio",
    "JUL": "julio",
    "AGO": "agosto",
    "SEP": "septiembre",
    "OCT": "octubre",
    "NOV": "noviembre",
    "DIC": "diciembre"
}

mapping_file_name_with_yfinance_tickers = {
    'SOY.CME_NOV': "ZSX", # soja noviembre
    'SOY.CME_ENE': "ZSF", # soja enero
    'SOY.CME_MAY': "ZSK", # soja mayo
    'SOY.CME_JUL': "ZSN", # soja julio
    'CRN.CME_DIC': "ZCZ", # maiz diciembre
    'CRN.CME_MAY': "ZCK", # maiz mayo
    'CRN.CME_JUL': "ZCN", # maiz julio
    'CRN.CME_SEP': "ZCU", # maix septiembre
}

valid_tickers = [
    "CRN.CME/DIC",
    "CRN.CME/JUL",
    "CRN.CME/MAY",
    "MAI.ROS/ABR",
    "MAI.ROS/DIC",
    "MAI.ROS/JUL",
    "MAI.ROS/SEP",
    "SOJ.ROS/ENE",
    "SOJ.ROS/JUL",
    "SOJ.ROS/MAY",
    "SOJ.ROS/NOV",
    "SOY.CME/ENE",
    "SOY.CME/JUL",
    "SOY.CME/MAY",
    "SOY.CME/NOV",
    "TRI.ROS/ENE",
    "TRI.ROS/JUL",
    "TRI.ROS/MAR",
    "TRI.ROS/DIC"
]


def get_pretty_names(file_name):
    commodity = mapping_names.get(file_name[:3], file_name[:3])
    market = mapping_names.get(file_name[4:7], file_name[4:7])
    month = mapping_names.get(file_name[8:], file_name[8:])

    return f'{commodity.upper()} {market.upper()} {month.upper()}'