# EA2 – Preprocesamiento y Limpieza de Datos

> ← [Volver al README general](../README.md)

## Objetivo

Implementar la etapa de preprocesamiento y limpieza de datos, simulando un entorno de Big Data en la nube:

- Cargar los datos ingestados en la EA1 (simulando un servicio cloud).
- Realizar análisis exploratorio e identificar problemas de calidad.
- Aplicar técnicas de limpieza y transformación de datos.
- Generar evidencias: datos limpios en Excel y reporte de auditoría `.txt`.
- Automatizar la ejecución mediante GitHub Actions.

**Script principal:** `src/cleaning.py`

---

## Trazabilidad del Proceso

### 1. Carga de Datos — Simulación de Entorno Cloud

En lugar de usar servicios reales de almacenamiento (Amazon S3, Azure Blob Storage, Google Cloud Storage), se utiliza la base de datos SQLite generada en la EA1 para **emular un servicio cloud de datos**.

Se carga la tabla `users` directamente desde `src/db/ingestion.db` a un DataFrame de Pandas, simulando la extracción distribuida propia de una plataforma Big Data.

```python
# ---- EA2 Paso 1: Carga de Datos desde la BD (Simulación de Entorno Cloud) ----
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df
```

---

### 2. Análisis Exploratorio y Validación

Se realiza un diagnóstico completo de calidad sobre los datos antes de cualquier transformación, documentando las estadísticas iniciales:

| Métrica analizada | Herramienta |
|:--|:--|
| Shape del DataFrame | `df.shape` |
| Tipos de datos actuales | `df.dtypes` |
| Registros duplicados | `df.duplicated().sum()` |
| Valores nulos por columna | `df.isnull().sum()` |
| Espacios en blanco innecesarios | `df[col] != df[col].str.strip()` |
| Emails no normalizados | `df['email'] != df['email'].str.lower()` |
| Estadísticas descriptivas | `df.describe(include='all')` |

```python
# ---- EA2 Paso 2: Análisis Exploratorio y Validación ----
def exploratory_analysis(df):
    stats = {}
    stats['duplicados'] = df.duplicated().sum()
    stats['nulos_por_columna'] = df.isnull().sum().to_dict()
    stats['emails_no_normalizados'] = (df['email'] != df['email'].str.lower()).sum()
    # ...
    return stats
```

**Resultados de la última ejecución:**
<!-- LOG_EXPLORE_START -->
```text
Nulos por col:
id          0
name        0
username    0
email       0
phone       0
website     0

Duplicados detectados: 0
Emails no normalizados (con mayúsculas): 10
```
<!-- LOG_EXPLORE_END -->

---

### 3. Limpieza y Transformación de Datos

Se aplica un **pipeline de limpieza integral** en cuatro categorías:

| # | Categoría | Operación | Técnica |
|:--|:--|:--|:--|
| 3a | Duplicados | Eliminación de registros duplicados | `drop_duplicates()` |
| 3b | Nulos | Imputación numérica con mediana | `fillna(mediana)` |
| 3b | Nulos | Imputación de texto con `'N/A'` | `fillna('N/A')` |
| 3c | Tipos | `id` asegurado como `INTEGER` | `astype(int)` |
| 3c | Tipos | Campos de texto asegurados como `STRING` | `astype(str)` |
| 3d | Transform. | Emails normalizados a minúsculas | `str.lower().str.strip()` |
| 3d | Transform. | Espacios en blanco eliminados | `str.strip()` |
| 3d | Transform. | Teléfonos estandarizados | regex sobre caracteres no válidos |
| 3d | Transform. | Websites normalizados a minúsculas | `str.lower().str.strip()` |

```python
# ---- EA2 Paso 3: Limpieza y Transformación de Datos ----
def clean_data(df, stats):
    df_clean = df.copy()
    # 3a. Eliminación de duplicados
    df_clean = df_clean.drop_duplicates()
    # 3b. Manejo de valores nulos (mediana o 'N/A')
    # 3c. Corrección de tipos de datos
    df_clean['id'] = df_clean['id'].astype(int)
    # 3d. Transformaciones adicionales
    df_clean['email'] = df_clean['email'].str.lower().str.strip()
    df_clean['phone'] = df_clean['phone'].str.replace(r'[^\d\s\-\+\(\)\.x]', '', regex=True)
    return df_clean, operaciones
```

**Registro de limpieza:**
<!-- LOG_CLEAN_START -->
```text
[LIMPIEZA] Duplicados eliminados: 0
[LIMPIEZA] Tipos corregidos: id→int, textos→str
[LIMPIEZA] Emails y websites → minúsculas, strip; teléfonos → estandarizados
```
<!-- LOG_CLEAN_END -->

---

### 4. Generación de Evidencias Complementarias

**Datos limpios (`src/xlsx/cleaned_data.xlsx`):**  
El DataFrame limpio completo se exporta a Excel, permitiendo su revisión directa por parte del instructor.

**Reporte de auditoría (`src/static/auditoria/cleaning_report.txt`):**  
Documento estructurado que incluye:
- Registros **antes** y **después** de la limpieza.
- Diagnóstico inicial (duplicados, nulos, inconsistencias detectadas).
- Lista numerada de cada operación de limpieza realizada.
- Tipos de datos finales de cada columna.
- Estado de integridad verificado.

```python
# ---- EA2 Paso 4b: Generación del Reporte de Auditoría ----
def generate_cleaning_report(original_df, cleaned_df, stats, operaciones):
    report = f"""
    Registros antes de limpieza:   {len(original_df)}
    Registros después de limpieza: {len(cleaned_df)}
    Operaciones realizadas: ...
    """
    with open(CLEANING_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
```

---

### 5. Automatización con GitHub Actions

El script de limpieza se ejecuta **después** del script de ingesta (EA1) dentro del mismo job, asegurando la secuencia correcta del pipeline de datos.

```yaml
# ---- EA2: Ejecución del script de preprocesamiento y limpieza ----
- name: Ejecutar script de limpieza (EA2)
  run: python src/cleaning.py

- name: Subir artefactos EA2 (Datos Limpios y Auditoría de Limpieza)
  uses: actions/upload-artifact@v4
  with:
    name: evidencias-cleaning
    path: |
      src/xlsx/cleaned_data.xlsx
      src/static/auditoria/cleaning_report.txt
```

---

## Archivos de Salida

| Archivo | Ruta | Descripción |
|:--|:--|:--|
| Datos limpios | `src/xlsx/cleaned_data.xlsx` | DataFrame limpio completo |
| Reporte auditoría | `src/static/auditoria/cleaning_report.txt` | Log de todas las operaciones |

---

## Ejecución Local

> **Prerequisito:** La EA1 debe haberse ejecutado primero para que exista `src/db/ingestion.db`.

```bash
# Paso 1: Ejecutar ingesta (EA1)
python src/ingestion.py

# Paso 2: Ejecutar limpieza (EA2)
python src/cleaning.py
```

---

## Criterios de Evaluación

| Competencia | Evidencia |
|:--|:--|
| **Automatización y Ejecución** | `bigdata.yml` ejecuta secuencialmente EA1 y EA2 sin errores, subiendo `evidencias-cleaning` como artefacto descargable desde GitHub Actions. |
| **Calidad del Preprocesamiento** | `cleaning.py` aplica deduplicación, imputación de nulos, corrección de tipos, normalización de emails/websites, estandarización de teléfonos y limpieza de espacios. |
| **Generación de Evidencias** | `cleaned_data.xlsx` con registros limpios y `cleaning_report.txt` enumerando cada operación, recuento antes/después y tipos de datos finales. |
| **Alojamiento y Documentación** | Proyecto en GitHub con estructura requerida. README documenta la trazabilidad completa, instrucciones y workflow. |
