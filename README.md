# Resolución de Tarea - Proyecto de Ingestión de Datos

Esta solución aborda la **"EA1. Ingestión de Datos desde un API"**. El objetivo de esta etapa es desarrollar un pipeline automatizado de ingesta de datos que sirva como cimiento fundamental para etapas futuras como preprocesamiento, enriquecimiento y modelado de Big Data.

## Interpretación de la Tarea y Descripción de la Solución

De acuerdo a las instrucciones dadas en la rúbrica, interpreto la tarea como la necesidad de crear un pequeño ducto de automatización (ETL básico) orientado a la extracción pura de una fuente en la web hacia un almacenamiento relacional estandarizado. 

He resuelto esto de la siguiente manera:
1. **Extracción (API):** El script `src/ingestion.py` se conecta al API pública `JSONPlaceholder` (usando el endpoint `/users` que devuelve perfiles de usuario, ideal para datos tabulares) y extrae sus datos en formato JSON mediante la librería `requests`.
2. **Almacenamiento (SQLite):** Los datos en memoria se vuelcan en una base de datos relacional local en la ruta descrita (`src/db/ingestion.db`). Se asegura de crear tablas sólo si no existen antes de realizar inserciones.
3. **Generación de Muestras (Pandas):** Para fines de revisión de datos dinámicas, el sistema lee la base de datos resultante a un DataFrame de Pandas y exporta una muestra tabular con las primeras filas en formato Excel (`src/xlsx/ingestion.xlsx`).
4. **Auditoría (.txt):** Como control de calidad, se genera un archivo de texto (`src/static/auditoria/ingestion.txt`) que certifica mediante recuento y validaciones que los datos en origen y los almacenados destino sean simétricos.
5. **Automatización (CI/CD):** Mediante GitHub Actions (`.github/workflows/bigdata.yml`), todo este proceso se vuelve auto-ejecutable y programable sin intervención manual cada vez que ocurren cambios en el código (`push`). Esto guarda las "evidencias" (db, excel, txt) como **Artefactos descargables** desde la pestaña Actions de dicho repositorio.

## Estructura del Proyecto

Se ha respetado la estructura de archivos/directorios solicitada para el entregable:

```text
proyecto_ingesta/
├── setup.py
├── README.md
├── .github
│   └── workflows
│       └── bigdata.yml
└── src
    ├── static
    │   └── auditoria
    │       └── ingestion.txt
    ├── db
    │   └── ingestion.db
    ├── xlsx
    │   └── ingestion.xlsx
    └── ingestion.py
```

## Instrucciones para Compilar / Ejecutar Localmente

### 1. Clonar e inicializar 
Teniendo este repositorio en tu ordenador, es recomendado inicializar un entorno virtual de python (opcional):
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac o bash
```

### 2. Instalar Dependencias
Instalar las librerías necesarias para la ejecución (mencionadas en `setup.py`):
```bash
pip install requests pandas openpyxl
```

### 3. Ejecutar el Script de Ingesta
Córrelo usando Python desde la raíz del proyecto:
```bash
python src/ingestion.py
```
   
Al finalizar la primera ejecución, observarás que se crean dinámicamente:
- La Base de Datos: `src/db/ingestion.db`
- La Muestra Excel: `src/xlsx/ingestion.xlsx`
- Auditoria de calidad: `src/static/auditoria/ingestion.txt`

### Validación por GitHub Actions
En el repositorio web (.github), el script se ejecuta en un servidor virtual de Ubuntu (acción: *ubuntu-latest*) de forma completamente desatendida, confirmando una vez más que todos los pasos se han emulado correctamente a nivel de automatización.
