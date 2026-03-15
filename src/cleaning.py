# EA2. Preprocesamiento y Limpieza de Datos – Proyecto Integrador Big Data
import os, sqlite3, pandas as pd, re
from datetime import datetime

# ---- EA2: Rutas ----
BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB     = os.path.join(BASE, 'src', 'db',             'ingestion.db')
XLSX   = os.path.join(BASE, 'src', 'xlsx',           'cleaned_data.xlsx')
REPORT = os.path.join(BASE, 'src', 'static', 'auditoria', 'cleaning_report.txt')
MD_DOC = os.path.join(BASE, 'docs', 'EA2_Cleaning.md')
for d in [os.path.dirname(XLSX), os.path.dirname(REPORT)]:
    os.makedirs(d, exist_ok=True)

def update_markdown(section_id, text_to_insert):
    if not os.path.exists(MD_DOC): return
    with open(MD_DOC, 'r', encoding='utf-8') as f: content = f.read()
    pattern = r'(<!-- LOG_' + section_id + r'_START -->\n)(.*?)(<!-- LOG_' + section_id + r'_END -->)'
    replacement = r'\1```text\n' + text_to_insert.replace('\\', '\\\\') + r'\n```\n\3'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open(MD_DOC, 'w', encoding='utf-8') as f: f.write(new_content)

# ---- EA2 Paso 1: Carga desde BD (simulación entorno cloud) ----
def load_data():
    print(f"\n[EA2] Conectando a BD: {DB}")
    conn = sqlite3.connect(DB)
    df   = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    print(f"[EA2] Datos cargados: {df.shape[0]} filas x {df.shape[1]} columnas")
    return df

# ---- EA2 Paso 2: Análisis exploratorio ----
def explore(df):
    print("\n[EA2] --- Análisis Exploratorio ---")
    log_text = f"Nulos por col:\n{df.isnull().sum().to_string()}\n\n"
    log_text += f"Duplicados detectados: {df.duplicated().sum()}\n"
    log_text += f"Emails no normalizados (con mayúsculas): {(df['email'] != df['email'].str.lower()).sum()}"
    print(log_text)
    update_markdown("EXPLORE", log_text)
    
    return {
        'total':       len(df),
        'duplicados':  int(df.duplicated().sum()),
        'nulos':       df.isnull().sum().to_dict(),
        'email_mayus': int((df['email'] != df['email'].str.lower()).sum()),
    }

# ---- EA2 Paso 3: Limpieza y transformación ----
def clean(df):
    print("\n[EA2] --- Limpieza ---")
    ops, d = [], df.copy()

    # 3a. Eliminación de duplicados
    antes = len(d); d = d.drop_duplicates()
    ops.append(f"Duplicados eliminados: {antes - len(d)}")

    # 3b. Manejo de valores nulos
    for col in d.columns:
        n = d[col].isnull().sum()
        if n:
            val = d[col].median() if d[col].dtype in ['int64','float64'] else 'N/A'
            d[col] = d[col].fillna(val)
            ops.append(f"Nulos en '{col}': {n} imputados con {val!r}")

    # 3c. Corrección de tipos
    d['id'] = d['id'].astype(int)
    for col in ['name','username','email','phone','website']:
        if col in d.columns: d[col] = d[col].astype(str)
    ops.append("Tipos corregidos: id→int, textos→str")

    # 3d. Transformaciones adicionales
    d['email']   = d['email'].str.lower().str.strip()
    d['website'] = d['website'].str.lower().str.strip()
    d['phone']   = d['phone'].str.replace(r'[^\d\s\-\+\(\)\.x]', '', regex=True)
    for col in ['name','username']: d[col] = d[col].str.strip()
    ops.append("Emails y websites → minúsculas, strip; teléfonos → estandarizados")

    log_text = ""
    for op in ops: 
        print(f"  ✔ {op}")
        log_text += f"[LIMPIEZA] {op}\n"
        
    print(f"\n[EA2] Registros tras limpieza: {len(d)}")
    update_markdown("CLEAN", log_text.strip())
    
    return d, ops

# ---- EA2 Paso 4a: Exportar datos limpios ----
def export(df):
    df.to_excel(XLSX, index=False)
    print(f"\n[EA2] Excel generado: {XLSX}  ({os.path.getsize(XLSX)} bytes)")

# ---- EA2 Paso 4b: Reporte de auditoría ----
def report(original, cleaned, stats, ops):
    ts  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    txt = (
        f"EA2 – REPORTE DE AUDITORÍA DE LIMPIEZA\nFecha: {ts}\n"
        f"{'─'*50}\n"
        f"Registros antes : {stats['total']}\n"
        f"Registros después: {len(cleaned)}\n"
        f"Eliminados       : {stats['total'] - len(cleaned)}\n"
        f"{'─'*50}\n"
        f"Diagnóstico inicial:\n"
        f"  Duplicados: {stats['duplicados']}\n"
        f"  Emails no normalizados: {stats['email_mayus']}\n"
        + "".join(f"  Nulos '{k}': {v}\n" for k,v in stats['nulos'].items()) +
        f"{'─'*50}\n"
        f"Operaciones realizadas:\n"
        + "".join(f"  {i+1}. {op}\n" for i,op in enumerate(ops)) +
        f"{'─'*50}\n"
        f"Estado: LIMPIEZA COMPLETADA CON ÉXITO ✅\n"
    )
    with open(REPORT, 'w', encoding='utf-8') as f: f.write(txt)
    print(f"[EA2] Reporte: {REPORT}  ({os.path.getsize(REPORT)} bytes)")
    print(txt)

# ---- EA2: Pipeline principal ----
if __name__ == '__main__':
    print(f"\n>>> EA2 INICIO: {datetime.now()}")
    try:
        print("::group::[EA2] Carga de Datos y Análisis Exploratorio")
        raw          = load_data()
        stats        = explore(raw)
        print("::endgroup::")
        
        print("::group::[EA2] Limpieza y Transformación")
        cleaned, ops = clean(raw)
        print("::endgroup::")
        
        print("::group::[EA2] Exportación y Reporte")
        export(cleaned)
        report(raw, cleaned, stats, ops)
        print(f"::notice title=Resultados EA2::Limpieza completada verificada. {len(cleaned)} registros.")
        print("::endgroup::")
        
        print(f">>> EA2 FIN: {datetime.now()}\n")
    except Exception as e:
        print(f"\n❌ EA2 ERROR: {e}"); raise
