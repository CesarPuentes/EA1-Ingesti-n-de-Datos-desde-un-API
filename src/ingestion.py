import os
import requests
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de directorios y rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DB_DIR = os.path.join(SRC_DIR, 'db')
XLSX_DIR = os.path.join(SRC_DIR, 'xlsx')
AUDIT_DIR = os.path.join(SRC_DIR, 'static', 'auditoria')

for d in [DB_DIR, XLSX_DIR, AUDIT_DIR]:
    os.makedirs(d, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, 'ingestion.db')
XLSX_PATH = os.path.join(XLSX_DIR, 'ingestion.xlsx')
AUDIT_PATH = os.path.join(AUDIT_DIR, 'ingestion.txt')
API_URL = "https://jsonplaceholder.typicode.com/users"

# Ejercicio 1: Lectura de Datos desde un API
def extract_data():
    print("-" * 50)
    print("EJERCICIO 1: EXTRACCIÓN DE DATOS API")
    print("-" * 50)
    print(f"[{datetime.now()}] Conectando a: {API_URL}")
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    print(f"[{datetime.now()}] Éxito: {len(data)} registros obtenidos")
    print(f"\nCampos JSON: {list(data[0].keys())}")
    print("Muestra (primeros 3):")
    for user in data[:3]:
        print(f"  ID: {user['id']} | {user['name']} | {user['email']}")
    print("-" * 50 + "\n")
    return data

# Ejercicio 2: Almacenamiento en SQLite
def save_to_db(data):
    print("-" * 50)
    print("EJERCICIO 2: ALMACENAMIENTO SQLITE")
    print("-" * 50)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creación de tabla (DDL)
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            email TEXT,
            phone TEXT,
            website TEXT
        )""")
    
    # Inserción (DML)
    for user in data:
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['name'], user['username'], user['email'], user['phone'], user['website']))
    conn.commit()

    # Verificación SQL
    print(f"[{datetime.now()}] Tabla 'users' actualizada.")
    
    print("\nQUERY: PRAGMA table_info(users)")
    cursor.execute("PRAGMA table_info(users)")
    for col in cursor.fetchall():
        print(f"  Col: {col[1]:<12} | Tipo: {col[2]}")

    print("\nQUERY: SELECT COUNT(*) FROM users")
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"  Total: {cursor.fetchone()[0]} registros en BD")

    print("\nQUERY: SELECT * FROM users (Vista rápida)")
    cursor.execute("SELECT * FROM users LIMIT 10")
    for row in cursor.fetchall():
        print(f"  {row}")

    conn.close()
    print("-" * 50 + "\n")

# Ejercicio 3a: Generación de Muestra con Pandas
def generate_sample():
    print("-" * 50)
    print("EJERCICIO 3a: MUESTRA CON PANDAS (XLSX)")
    print("-" * 50)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    print(f"[{datetime.now()}] DataFrame cargado: {df.shape}")
    print("\nTipos de datos Pandas:")
    print(df.dtypes)
    
    print("\nMuestra del DataFrame (to_string):")
    print(df.head(10).to_string(index=False))

    print("\nEstadísticas (describe):")
    print(df.describe(include='all').to_string())

    df.head(10).to_excel(XLSX_PATH, index=False)
    print(f"\n[{datetime.now()}] Archivo XLSX generado: {XLSX_PATH}")
    print("-" * 50 + "\n")
    return df

# Ejercicio 3b: Archivo de Auditoría
def generate_audit(api_data, db_df):
    print("-" * 50)
    print("EJERCICIO 3b: REPORTE DE AUDITORÍA (.TXT)")
    print("-" * 50)
    
    api_count = len(api_data)
    db_count = len(db_df)
    
    audit_content = f"""--- REPORTE DE AUDITORÍA ---
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
API: {API_URL}

1. Conteo de Registros:
 - API: {api_count}
 - BD: {db_count}
ESTADO: {'ÉXITO' if api_count == db_count else 'ADVERTENCIA'}

2. Verificación:
 - SQLite e integridad OK.
 - Archivo XLSX generado."""

    with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
        f.write(audit_content)

    print("Contenido del archivo .txt:")
    print(audit_content)
    print("-" * 50 + "\n")

# Ejercicio 4: Verificación Final
def verify_files():
    print("-" * 50)
    print("VERIFICACIÓN DE ARCHIVOS")
    print("-" * 50)
    files = [("DB", DB_PATH), ("Excel", XLSX_PATH), ("Audit", AUDIT_PATH)]
    for name, path in files:
        status = "✅" if os.path.exists(path) else "❌"
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"{status} {name:<6}: {size} bytes en {path}")
    print("-" * 50 + "\n")

if __name__ == "__main__":
    print(f"\n>>> INICIANDO PROCESO: {datetime.now()}\n")
    try:
        api_data = extract_data()
        save_to_db(api_data)
        db_df = generate_sample()
        generate_audit(api_data, db_df)
        verify_files()
        print(f">>> PROCESO FINALIZADO CON ÉXITO: {datetime.now()}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
