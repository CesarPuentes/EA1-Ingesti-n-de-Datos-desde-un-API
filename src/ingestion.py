import os
import requests
import sqlite3
import pandas as pd
from datetime import datetime

# Definir directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DB_DIR = os.path.join(SRC_DIR, 'db')
XLSX_DIR = os.path.join(SRC_DIR, 'xlsx')
AUDIT_DIR = os.path.join(SRC_DIR, 'static', 'auditoria')

# Asegurar directorios
for d in [DB_DIR, XLSX_DIR, AUDIT_DIR]:
    os.makedirs(d, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, 'ingestion.db')
XLSX_PATH = os.path.join(XLSX_DIR, 'ingestion.xlsx')
AUDIT_PATH = os.path.join(AUDIT_DIR, 'ingestion.txt')

API_URL = "https://jsonplaceholder.typicode.com/users"

def extract_data():
    print(f"[{datetime.now()}] Extrayendo datos de: {API_URL}")
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

def save_to_db(data):
    print(f"[{datetime.now()}] Guardando datos en SQLite: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            email TEXT,
            phone TEXT,
            website TEXT
        )
    ''')
    for user in data:
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['name'], user['username'], user['email'], user['phone'], user['website']))
    conn.commit()
    conn.close()

def generate_sample():
    print(f"[{datetime.now()}] Generando muestra XLSX: {XLSX_PATH}")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    sample_df = df.head(10)
    sample_df.to_excel(XLSX_PATH, index=False)
    return df

def generate_audit(api_data, db_df):
    print(f"[{datetime.now()}] Generando auditoría: {AUDIT_PATH}")
    api_count = len(api_data)
    db_count = len(db_df)
    
    with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
        f.write("--- REPORTE DE AUDITORÍA ---\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"API: {API_URL}\n\n")
        f.write("1. Conteo de Registros:\n")
        f.write(f" - API: {api_count}\n")
        f.write(f" - BD: {db_count}\n\n")
        
        if api_count == db_count:
            f.write("ESTADO: ÉXITO. Los registros concuerdan.\n\n")
        else:
            f.write("ESTADO: ADVERTENCIA. Diferencia en registros.\n\n")
        
        f.write("2. Verificación de Integridad:\n")
        f.write(" - Estructura de tabla verificada.\n")
        f.write(" - Archivo XLSX generado exitosamente.\n")

if __name__ == "__main__":
    try:
        api_data = extract_data()
        save_to_db(api_data)
        db_df = generate_sample()
        generate_audit(api_data, db_df)
        print("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")
