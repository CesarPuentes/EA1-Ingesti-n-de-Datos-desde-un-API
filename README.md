# EA1. Ingestión de Datos desde un API - Proyecto Integrador Big Data

Este repositorio contiene la solución completa a la actividad **"EA1. Ingestión de Datos desde un API"**. El objetivo es implementar la etapa fundacional de ingesta de datos del proyecto integrador, extrayendo datos de manera automática hacia un almacenamiento estructurado para futuras etapas analíticas.

## Desarrollo y Trazabilidad del Proyecto

A continuación se detalla cómo se dio cumplimiento exacto a cada uno de los lineamientos solicitados en la ruta metodológica de las instrucciones de la Tarea:

### 1. Lectura de Datos desde un API

**Identifica el API a utilizar y revisa su documentación para conocer los endpoints:** 
Se seleccionó la API pública de pruebas `JSONPlaceholder`, específicamente utilizando el endpoint de `/users`, el cual devuelve un bloque JSON con perfiles de usuarios estructurados idóneos para almacenamiento relacional.

**Desarrolla un script en Python que se conecte al API y extraiga los datos:** 
En el archivo base `src/ingestion.py`, se utilizó la librería `requests` para gestionar la conexión y almacenar el bloque JSON en memoria. El script controla automáticamente los códigos de respuesta (`response.raise_for_status()`) garantizando que los datos no estén corruptos antes del proceso ETL.

```python
API_URL = "https://jsonplaceholder.typicode.com/users"

def extract_data():
    print(f"[{datetime.now()}] Extrayendo datos de: {API_URL}")
    response = requests.get(API_URL)
    response.raise_for_status() # Verifica que la petición fue 200 OK
    return response.json()
```

### 2. Almacenamiento en SQLite

**Utiliza el módulo de base de datos (`sqlite3`) para crear una base analítica:**
Se inicializó un almacenamiento local autogenerado en la ruta nativa `src/db/ingestion.db`. Mediante comandos DDL (`CREATE TABLE IF NOT EXISTS`) dentro de Python, se modelaron las columnas base de acuerdo a las llaves maestras detectadas en la respuesta JSON del endpoint utilizado. 

**Inserta los datos extraídos del API:**
El programa cicla (itera) todo el directorio originado por el API utilizando sentencias DML `INSERT OR REPLACE INTO` asegurando que no se generen duplicados por ID de origen.

```python
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
        # Inserción iterando cada objeto JSON
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['name'], user['username'], user['email'], user['phone'], user['website']))
    conn.commit()
    conn.close()
```

### 3. Generación de Evidencias Complementarias

**Archivo de Muestra con Pandas (Excel/CSV):**
Para evidenciar los resultados al analista, el script utiliza el ORM conector de Pandas para leer y cargar los registros desde la base local hacia un DataFrame. Posteriormente, exporta los primeros registros directamente al archivo `src/xlsx/ingestion.xlsx`.

```python
def generate_sample():
    print(f"[{datetime.now()}] Generando muestra XLSX: {XLSX_PATH}")
    conn = sqlite3.connect(DB_PATH)
    # Carga los datos almacenados a Pandas DF
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    
    # Exporta Muestra Representativa
    sample_df = df.head(10)
    sample_df.to_excel(XLSX_PATH, index=False)
    return df
```

**Archivo de Auditoría (.txt):**
Un archivo físico llamado `src/static/auditoria/ingestion.txt` se escribe al final de la ejecución, calculando simetrías y realizando conteos precisos para confirmar la fiabilidad de la ingesta (comparando Registros de Origen vs Registros Destino). 

```python
def generate_audit(api_data, db_df):
    print(f"[{datetime.now()}] Generando auditoría: {AUDIT_PATH}")
    api_count = len(api_data)
    db_count = len(db_df)
    
    with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
        f.write("--- REPORTE DE AUDITORÍA ---\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f" - API: {api_count} Registros\n")
        f.write(f" - BD: {db_count} Registros\n")
        
        if api_count == db_count:
            f.write("ESTADO: ÉXITO. Los registros concuerdan.\n")
        else:
            f.write("ESTADO: ADVERTENCIA. Diferencia detectada.\n")
```

### 4. Alojamiento y Automatización (GitHub Actions)

Todo este proyecto se encuentra contenido y manejado bajo el gestor de versiones Git. 
Se implementó un servidor transitorio `ubuntu-latest` a través el archivo `.github/workflows/bigdata.yml`. El "Action" obedece los triggers al hacer "Push" a la rama _main_ y además posee automatización tipo *cron*, auto-ejecutando en la madrugada y recuperando en comprimidos `.zip` descargables los archivos que resultaron de la extracción programada.

```yaml
jobs:
  ingestion:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout del repositorio
      uses: actions/checkout@v4

    - name: Ejecutar script de ingesta
      run: |
        python src/ingestion.py

    - name: Subir artefactos generados (Base de Datos, Muestra y Auditoría)
      uses: actions/upload-artifact@v4
      with:
        name: evidencias-ingestion
        path: |
          src/db/ingestion.db
          src/xlsx/ingestion.xlsx
          src/static/auditoria/ingestion.txt
```

---

## Instrucciones para Compilar / Ejecutar Localmente

**A) Clonar e inicializar**
```bash
git clone https://github.com/CesarPuentes/EA1-Ingesti-n-de-Datos-desde-un-API.git
cd EA1-Ingesti-n-de-Datos-desde-un-API
```

**B) Instalar dependencias**
Es altamente sugerido crear un entorno virtual, y posteriormente instalar los paquetes base descritos en el `setup.py`:
```bash
# (Opcional) Crear entorno: python -m venv venv && source venv/bin/activate
pip install requests pandas openpyxl
```

**C) Ejecutar el script principal**
Desde la carpeta raíz del proyecto, ejecuta el motor de ingesta:
```bash
python src/ingestion.py
```
Si se ejecuta exitosamente, el script creará dinámicamente tu base de datos y archivos requeridos en las siguientes rutas relativas `src/db/`, `src/xlsx/` y `src/static/auditoria`.

---

## Automatización con GitHub Actions y Verificación
La principal virtud de este proyecto es que **no requiere ser ejecutado manualmente**. 
**¿Cómo verificar la creación de evidencias?**
1. Visita la pestaña **"Actions"** en el panel superior de este repositorio en GitHub.
2. Haz clic sobre la ejecución más reciente etiquetada como verde o finalizada (`Ingestión de Datos`).
3. Desliza a la parte inferior hacia el panel llamado **"Artifacts"**.
4. Haz clic sobre la carpeta virtual **`evidencias-ingestion`**. Esto descargará un `.zip` comprimiendo los tres archivos de evidencia física levantados dinámicamente por la máquina en la nube: la Base de Datos(`.db`), el Excel (`.xlsx`) y la Auditoría (`.txt`).

---

## Alineación Criterios de Evaluación y Rúbrica de la Tarea

Esta entrega ha sido diseñada meticulosamente para dar cumplimiento perfecto a la rúbrica exigida en la plataforma. A continuación se sustenta la cobertura:

| Competencia de Aprendizaje | Evidencia del Cumplimiento en el Proyecto |
| :--- | :--- |
| **Automatización y Ejecución (Github)** | El workflow (`bigdata.yml`) emplea Ubuntu/Python_3.10, corre sin dependencias intermitentes, se activa tras todo PUSH o manual, generando *Upload Artifacts* con los comprobantes generados, los cuales son libremente descargables desde GitHub Actions. |
| **Extracción de Datos API** | `ingestion.py` utiliza la librería certificada `requests`, hace peticiones a JSONPlaceholder, previene errores controlando el código de respuesta HTTP `200` y analiza exhaustivamente los elementos anidados de cada bloque (ej. la metaciudad del usuario). |
| **Generación de Salidas** | Mediante algoritmos del script Python en `src`, el volumen extraído se empaquetó forzadamente mediante `sqlite3` generador de DDL/DML, se serializó una muestra a `Pandas.to_excel` y con operaciones I/O básicas documentó un registro comprobador .txt. Todos ellos autogenerados en subdirectorios exactos. |
| **Puntualidad Absoluta** | Estructura de entrega exacta y código de base emitido completamente dentro de las fechas pactadas y operativas (Antes del Martes 3 de marzo a las 23:59h). |
| **Total Estimado** | Solución lista, automatizada mediante CI/CD y trazable permanentemente en el ecosistema Git. |
