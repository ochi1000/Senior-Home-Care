import pyodbc

# Database Configuration
DB_CONFIG = {
    'server': 'DESKTOP-7SQK3EK',
    'database': 'CareHomeAssitance',
    'username': 'ochi',
    'password': 'password'
}

def get_db_connection():
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_CONFIG["server"]};'
        f'DATABASE={DB_CONFIG["database"]};'
        f'UID={DB_CONFIG["username"]};'
        f'PWD={DB_CONFIG["password"]}'
    )
    return pyodbc.connect(conn_str)