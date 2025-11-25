import pyodbc

server = '192.168.7.17'
port = 5000
database = 'bdtec'
username = 'root'
password = 'Chingatumadre_123'

connection_string = (
    "DRIVER={FreeTDS};"
    f"SERVER={server};"
    f"PORT={port};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "TDS_Version=8.0;"
)

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

cursor.execute("SELECT TOP 5 * FROM alumnos")
for row in cursor.fetchall():
    print(row)

conn.close()
