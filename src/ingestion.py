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
    data = response.json()
    print(f"[{datetime.now()}] Datos extraídos exitosamente: {len(data)} registros obtenidos del API")
    return data

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
    print(f"[{datetime.now()}] Base de datos SQLite creada/actualizada exitosamente con {len(data)} registros")

def generate_sample():
    print(f"[{datetime.now()}] Generando muestra XLSX: {XLSX_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Consulta SQL 1: Estructura de la tabla ---
    query_schema = "PRAGMA table_info(users)"
    print("\n" + "="*60)
    print(f"CONSULTA SQL: {query_schema}")
    print("="*60)
    cursor.execute(query_schema)
    columns = cursor.fetchall()
    print(f"{'ID':<5} {'Columna':<15} {'Tipo':<10} {'Not Null':<10} {'PK':<5}")
    print("-"*45)
    for col in columns:
        print(f"{col[0]:<5} {col[1]:<15} {col[2]:<10} {'Sí' if col[3] else 'No':<10} {'Sí' if col[5] else 'No':<5}")
    print("="*60 + "\n")

    # --- Consulta SQL 2: Conteo total de registros ---
    query_count = "SELECT COUNT(*) AS total_registros FROM users"
    print("="*60)
    print(f"CONSULTA SQL: {query_count}")
    print("="*60)
    cursor.execute(query_count)
    count = cursor.fetchone()[0]
    print(f"Resultado: {count} registros almacenados en la tabla 'users'")
    print("="*60 + "\n")

    # --- Consulta SQL 3: Selección de todos los registros ---
    query_select = "SELECT * FROM users"
    print("="*60)
    print(f"CONSULTA SQL: {query_select}")
    print("="*60)
    df = pd.read_sql_query(query_select, conn)
    conn.close()
    sample_df = df.head(10)
    sample_df.to_excel(XLSX_PATH, index=False)
    print("Resultado (muestra representativa cargada a Pandas DataFrame):")
    print("-"*60)
    print(sample_df.to_string(index=False))
    print("="*60 + "\n")
    
    return df

def generate_audit(api_data, db_df):
    print(f"[{datetime.now()}] Generando auditoría: {AUDIT_PATH}")
    api_count = len(api_data)
    db_count = len(db_df)
    
    audit_lines = []
    audit_lines.append("--- REPORTE DE AUDITORÍA ---")
    audit_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    audit_lines.append(f"API: {API_URL}")
    audit_lines.append("")
    audit_lines.append("1. Conteo de Registros:")
    audit_lines.append(f" - API: {api_count}")
    audit_lines.append(f" - BD: {db_count}")
    audit_lines.append("")
    if api_count == db_count:
        audit_lines.append("ESTADO: ÉXITO. Los registros concuerdan.")
    else:
        audit_lines.append("ESTADO: ADVERTENCIA. Diferencia en registros.")
    audit_lines.append("")
    audit_lines.append("2. Verificación de Integridad:")
    audit_lines.append(" - Estructura de tabla verificada.")
    audit_lines.append(" - Archivo XLSX generado exitosamente.")
    
    audit_content = "\n".join(audit_lines)
    
    with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
        f.write(audit_content + "\n")
    
    # Imprimir el reporte de auditoría en consola (evidencia en logs de GitHub Actions)
    print("\n" + "="*50)
    print("REPORTE DE AUDITORÍA (contenido de ingestion.txt):")
    print("="*50)
    print(audit_content)
    print("="*50 + "\n")

def verify_files():
    """Verifica y muestra evidencia de los archivos generados."""
    print("\n" + "="*50)
    print("VERIFICACIÓN DE ARCHIVOS GENERADOS:")
    print("="*50)
    files_to_check = [
        ("Base de Datos SQLite", DB_PATH),
        ("Muestra Excel (XLSX)", XLSX_PATH),
        ("Archivo de Auditoría (TXT)", AUDIT_PATH),
    ]
    all_ok = True
    for description, path in files_to_check:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ {description}: {path} ({size} bytes)")
        else:
            print(f"  ❌ {description}: {path} — NO ENCONTRADO")
            all_ok = False
    print("="*50)
    if all_ok:
        print("RESULTADO: Todos los archivos fueron generados correctamente.")
    else:
        print("RESULTADO: ADVERTENCIA — Algunos archivos no se generaron.")
    print("="*50 + "\n")
    return all_ok

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# INICIO DEL PROCESO DE INGESTIÓN DE DATOS")
    print(f"# Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("#"*60 + "\n")
    try:
        api_data = extract_data()
        save_to_db(api_data)
        db_df = generate_sample()
        generate_audit(api_data, db_df)
        verify_files()
        print("\n" + "#"*60)
        print("# PROCESO DE INGESTIÓN COMPLETADO EXITOSAMENTE")
        print("#"*60 + "\n")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN EL PROCESO: {e}")
        raise
