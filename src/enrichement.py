# EA3. Enriquecimiento de Datos – Proyecto Integrador Big Data
import os, pandas as pd
from datetime import datetime

# ---- Rutas ----
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC     = os.path.join(BASE, 'src')
DATA    = os.path.join(SRC, 'data')
DB_PATH = os.path.join(SRC, 'db', 'ingestion.db')
CLEAN   = os.path.join(SRC, 'xlsx', 'cleaned_data.xlsx')
OUT_XLS = os.path.join(SRC, 'xlsx', 'enriched_data.xlsx')
REPORT  = os.path.join(SRC, 'static', 'auditoria', 'enriched_report.txt')
for d in [os.path.dirname(OUT_XLS), os.path.dirname(REPORT)]:
    os.makedirs(d, exist_ok=True)

MD_DOC = os.path.join(BASE, 'docs', 'EA3_Enrichment.md')

def update_markdown(section_id, text_to_insert):
    if not os.path.exists(MD_DOC): return
    import re
    with open(MD_DOC, 'r', encoding='utf-8') as f: content = f.read()
    pattern = r'(<!-- LOG_' + section_id + r'_START -->\n)(.*?)(<!-- LOG_' + section_id + r'_END -->)'
    # Only replace if the markers actually exist in the file
    if re.search(pattern, content, flags=re.DOTALL):
        replacement = r'\1```text\n' + text_to_insert.replace('\\', '\\\\') + r'\n```\n\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(MD_DOC, 'w', encoding='utf-8') as f: f.write(new_content)

# ---- Paso 1: Cargar dataset limpio (EA2) ----
def load_base():
    print(f"[EA3] Cargando dataset limpio: {CLEAN}")
    df = pd.read_excel(CLEAN)
    print(f"[EA3] Dataset base: {df.shape[0]} filas × {df.shape[1]} columnas")
    print(f"[EA3] Columnas: {list(df.columns)}")
    return df

# ---- Paso 2: Leer fuentes adicionales (6 formatos) ----
def read_sources():
    """Lee cada fuente y devuelve lista de (nombre, formato, DataFrame)."""
    sources = []

    # 1. JSON
    path = os.path.join(DATA, 'departments.json')
    df = pd.read_json(path)
    sources.append(('departments', 'JSON', df))
    print(f"  📄 JSON  → departments.json   | {len(df)} registros | cols: {list(df.columns)}")

    # 2. XLSX
    path = os.path.join(DATA, 'salaries.xlsx')
    df = pd.read_excel(path)
    sources.append(('salaries', 'XLSX', df))
    print(f"  📄 XLSX  → salaries.xlsx      | {len(df)} registros | cols: {list(df.columns)}")

    # 3. CSV
    path = os.path.join(DATA, 'locations.csv')
    df = pd.read_csv(path)
    sources.append(('locations', 'CSV', df))
    print(f"  📄 CSV   → locations.csv       | {len(df)} registros | cols: {list(df.columns)}")

    # 4. XML
    path = os.path.join(DATA, 'skills.xml')
    df = pd.read_xml(path, xpath='.//user')
    sources.append(('skills', 'XML', df))
    print(f"  📄 XML   → skills.xml          | {len(df)} registros | cols: {list(df.columns)}")

    # 5. HTML
    path = os.path.join(DATA, 'projects.html')
    dfs = pd.read_html(path)
    df = dfs[0]
    sources.append(('projects', 'HTML', df))
    print(f"  📄 HTML  → projects.html       | {len(df)} registros | cols: {list(df.columns)}")

    # 6. TXT (delimitado por pipe)
    path = os.path.join(DATA, 'notes.txt')
    df = pd.read_csv(path, sep='|')
    sources.append(('notes', 'TXT', df))
    print(f"  📄 TXT   → notes.txt           | {len(df)} registros | cols: {list(df.columns)}")

    return sources

# ---- Paso 3: Cruce e integración (merge por id) ----
def enrich(base, sources):
    """Left join de cada fuente sobre el dataset base usando 'id'."""
    log = []
    df = base.copy()
    original_cols = list(df.columns)

    for name, fmt, src in sources:
        before = len(df)
        # Asegurar tipo int para la clave de cruce
        src['id'] = src['id'].astype(int)
        merged = df.merge(src, on='id', how='left')
        new_cols = [c for c in merged.columns if c not in df.columns]
        matched  = merged[new_cols[0]].notna().sum() if new_cols else 0

        entry = (
            f"Fuente '{name}' ({fmt}): {len(src)} registros leídos, "
            f"{matched}/{len(df)} coincidencias, columnas añadidas: {new_cols}"
        )
        log.append(entry)
        print(f"  ✔ {entry}")
        df = merged

    added_cols = [c for c in df.columns if c not in original_cols]
    print(f"\n[EA3] Enriquecimiento completado: {df.shape[0]} filas × {df.shape[1]} columnas")
    print(f"[EA3] Columnas añadidas: {added_cols}")
    
    # Prepara el texto para el log dinámico en markdown
    log_text = ""
    for entry in log:
        log_text += f"✔ {entry}\n"
    update_markdown("ENRICH", log_text.strip())
    
    return df, log

# ---- Paso 4a: Exportar dataset enriquecido ----
def export(df):
    df.to_excel(OUT_XLS, index=False)
    print(f"\n[EA3] Excel generado: {OUT_XLS}  ({os.path.getsize(OUT_XLS)} bytes)")

# ---- Paso 4b: Reporte de auditoría ----
def report(base, enriched, log):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    txt = (
        f"EA3 – REPORTE DE AUDITORÍA DE ENRIQUECIMIENTO\n"
        f"Fecha: {ts}\n"
        f"{'─'*55}\n"
        f"Registros dataset base : {len(base)}\n"
        f"Registros enriquecido  : {len(enriched)}\n"
        f"Columnas originales    : {list(base.columns)}\n"
        f"Columnas finales       : {list(enriched.columns)}\n"
        f"Columnas añadidas      : {[c for c in enriched.columns if c not in base.columns]}\n"
        f"{'─'*55}\n"
        f"Detalle por fuente:\n"
        + "".join(f"  {i+1}. {entry}\n" for i, entry in enumerate(log))
        + f"{'─'*55}\n"
        f"Formatos integrados    : JSON, XLSX, CSV, XML, HTML, TXT\n"
        f"Clave de cruce         : id\n"
        f"Tipo de join           : LEFT JOIN\n"
        f"{'─'*55}\n"
        f"Estado: ENRIQUECIMIENTO COMPLETADO CON ÉXITO ✅\n"
    )
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(f"[EA3] Reporte: {REPORT}  ({os.path.getsize(REPORT)} bytes)")
    print(txt)

# ---- Pipeline principal ----
if __name__ == '__main__':
    print(f"\n>>> EA3 INICIO: {datetime.now()}")
    try:
        print("::group::[EA3] Carga del Dataset Base")
        base = load_base()
        print("::endgroup::")

        print("::group::[EA3] Lectura de Fuentes Adicionales (6 formatos)")
        sources = read_sources()
        print("::endgroup::")

        print("::group::[EA3] Cruce e Integración de Datos")
        enriched, log = enrich(base, sources)
        print("::endgroup::")

        print("::group::[EA3] Exportación y Reporte de Auditoría")
        export(enriched)
        report(base, enriched, log)
        print(f"::notice title=Resultados EA3::Enriquecimiento completado. "
              f"{len(enriched)} registros, {len(enriched.columns)} columnas.")
        print("::endgroup::")

        print(f">>> EA3 FIN: {datetime.now()}\n")
    except Exception as e:
        print(f"\n❌ EA3 ERROR: {e}"); raise
