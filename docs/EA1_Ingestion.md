# EA1 – Ingestión de Datos desde un API

> ← [Volver al README general](../README.md)

## Objetivo

Implementar la etapa de ingesta de datos del proyecto integrador de Big Data:

- Leer datos desde un API público.
- Almacenarlos en una base de datos SQLite.
- Generar evidencias: muestra en Excel y archivo de auditoría `.txt`.
- Automatizar la ejecución mediante GitHub Actions.

**Script principal:** `src/ingestion.py`

---

## Trazabilidad del Proceso

### 1. Lectura de Datos desde un API

Se seleccionó la API pública de pruebas **JSONPlaceholder**, endpoint `/users`, que devuelve 10 perfiles de usuarios en formato JSON — estructura ideal para almacenamiento relacional.

Se usó la librería `requests` para gestionar la conexión. El script controla automáticamente los códigos de respuesta (`response.raise_for_status()`) garantizando que los datos no estén corruptos antes del proceso ETL.

```python
API_URL = "https://jsonplaceholder.typicode.com/users"

def extract_data():
    response = requests.get(API_URL)
    response.raise_for_status()  # Valida código HTTP 200
    return response.json()
```

![git1](../git1.png)

---

### 2. Almacenamiento en SQLite

Se crea la base de datos `src/db/ingestion.db` dinámicamente. Mediante DDL (`CREATE TABLE IF NOT EXISTS`) se modela la tabla `users` con las columnas extraídas del JSON.

La inserción usa `INSERT OR REPLACE INTO` para evitar duplicados por `id` de origen.

```python
def save_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT, username TEXT,
            email TEXT, phone TEXT, website TEXT
        )
    ''')
    for user in data:
        cursor.execute(
            'INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?)',
            (user['id'], user['name'], user['username'],
             user['email'], user['phone'], user['website'])
        )
    conn.commit()
    conn.close()
```

![git2](../git2.png)

---

### 3. Generación de Evidencias Complementarias

**Archivo de muestra Excel (`src/xlsx/ingestion.xlsx`):**  
Se carga la tabla `users` a un DataFrame de Pandas y se exportan los primeros 10 registros al archivo Excel.

**Archivo de auditoría (`src/static/auditoria/ingestion.txt`):**  
Se comparan los registros del API contra los almacenados en la BD, registrando conteos y estado de integridad.

```python
def generate_audit(api_data, db_df):
    api_count = len(api_data)
    db_count = len(db_df)
    estado = 'ÉXITO' if api_count == db_count else 'ADVERTENCIA'
    # Escribe reporte en ingestion.txt
```

![git3](../git3.png)

---

### 4. Automatización con GitHub Actions

El workflow `.github/workflows/bigdata.yml` ejecuta el script automáticamente en cada `push` a `main`, por cron diario, y manualmente desde la interfaz de GitHub.

```yaml
# ---- EA1: Ejecución del script de ingesta ----
- name: Ejecutar script de ingesta (EA1)
  run: python src/ingestion.py

- name: Subir artefactos EA1 (Base de Datos, Muestra y Auditoría)
  uses: actions/upload-artifact@v4
  with:
    name: evidencias-ingestion
    path: |
      src/db/ingestion.db
      src/xlsx/ingestion.xlsx
      src/static/auditoria/ingestion.txt
```

---

## Archivos de Salida

| Archivo | Ruta | Descripción |
|:--|:--|:--|
| Base de datos | `src/db/ingestion.db` | SQLite con tabla `users` |
| Muestra Excel | `src/xlsx/ingestion.xlsx` | Primeros 10 registros |
| Auditoría | `src/static/auditoria/ingestion.txt` | Comparación API vs BD |

---

## Ejecución Local

```bash
# Instalar dependencias
pip install requests pandas openpyxl

# Ejecutar ingesta
python src/ingestion.py
```

---

## Criterios de Evaluación

| Competencia | Evidencia |
|:--|:--|
| **Automatización y Ejecución (GitHub)** | `bigdata.yml` con Ubuntu/Python 3.10, triggers en push/cron/manual, artefactos descargables desde GitHub Actions. |
| **Extracción de Datos API** | `ingestion.py` usa `requests`, valida HTTP 200 con `raise_for_status()`, extrae y mapea campos JSON a columnas relacionales. |
| **Generación de Salidas** | SQLite con DDL/DML, muestra exportada con `pandas.to_excel()`, auditoría de integridad `.txt` autogenerada. |
| **Puntualidad y Entrega** | Estructura de entrega exacta dentro de las fechas pactadas. |
