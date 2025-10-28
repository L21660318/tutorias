import pyodbc

# Datos de conexión
server = '192.168.7.17'   # dirección IP o nombre del servidor
port = 5000                # puerto de Sybase
database = 'bdtec'
username = 'root'
password = 'Chingatumadre_123'

# Conexión a Sybase (FreeTDS o driver oficial)
connection_string = f'DRIVER={{Adaptive Server Enterprise}};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};'
# Si usas FreeTDS en Linux:
# connection_string = f'DRIVER={{FreeTDS}};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TDS_Version=8.0;'

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Prueba de consulta
cursor.execute("SELECT TOP 5 * FROM alumnos")
for row in cursor.fetchall():
    print(row)

conn.close()
