# EA3 – Enriquecimiento de Datos en Plataforma de Big Data en la Nube

> ← [Volver al README general](../README.md)

## Objetivo

Implementar la etapa de enriquecimiento de datos del proyecto integrador de Big Data:

- Cargar el conjunto de datos limpio generado en la Actividad 2.
- Integrar información adicional proveniente de múltiples fuentes y formatos (JSON, XLSX, CSV, XML, HTML, TXT).
- Generar evidencias: dataset enriquecido en Excel y reporte de auditoría `.txt`.
- Automatizar la ejecución mediante GitHub Actions.

**Script principal:** `src/enrichement.py`

---

## Trazabilidad del Proceso — Ruta Metodológica

### 1. Carga del Dataset Base

Se cargan los datos limpios generados en la Actividad 2, almacenados en `src/xlsx/cleaned_data.xlsx`. Este archivo actúa como la **simulación del entorno cloud**, tal como se ha hecho en las actividades previas.

Se utiliza **Pandas** (`pd.read_excel`) para leer el archivo directamente al DataFrame base, obteniendo los 10 registros limpios con 6 columnas originales: `id`, `name`, `username`, `email`, `phone`, `website`.

```python
# ---- Paso 1: Cargar dataset limpio (EA2) ----
def load_base():
    df = pd.read_excel(CLEAN)   # cleaned_data.xlsx
    return df
```

---

### 2. Lectura de Fuentes Adicionales

Se prepararon **6 archivos complementarios** en distintos formatos, almacenados en `src/data/`. Cada uno aporta columnas nuevas al dataset base y se vincula mediante la columna `id`.

| # | Archivo | Formato | Función Pandas | Columnas añadidas |
|:-:|---------|---------|----------------|-------------------|
| 1 | `departments.json` | JSON | `pd.read_json()` | `department`, `role` |
| 2 | `salaries.xlsx` | XLSX | `pd.read_excel()` | `salary`, `currency` |
| 3 | `locations.csv` | CSV | `pd.read_csv()` | `city`, `country` |
| 4 | `skills.xml` | XML | `pd.read_xml(xpath='.//user')` | `primary_skill`, `level` |
| 5 | `projects.html` | HTML | `pd.read_html()[0]` | `project`, `hours` |
| 6 | `notes.txt` | TXT (pipe `\|`) | `pd.read_csv(sep='\|')` | `notes` |

Cada fuente se lee de forma individual y se almacena como un DataFrame independiente antes de la integración:

```python
# ---- Paso 2: Leer fuentes adicionales (6 formatos) ----
def read_sources():
    sources = []
    # 1. JSON
    sources.append(('departments', 'JSON', pd.read_json('departments.json')))
    # 2. XLSX
    sources.append(('salaries', 'XLSX', pd.read_excel('salaries.xlsx')))
    # 3. CSV
    sources.append(('locations', 'CSV', pd.read_csv('locations.csv')))
    # 4. XML
    sources.append(('skills', 'XML', pd.read_xml('skills.xml', xpath='.//user')))
    # 5. HTML
    sources.append(('projects', 'HTML', pd.read_html('projects.html')[0]))
    # 6. TXT (delimitado por pipe)
    sources.append(('notes', 'TXT', pd.read_csv('notes.txt', sep='|')))
    return sources
```

---

### 3. Cruce e Integración de Datos

#### Clave de unión

Se utiliza la columna **`id`** como clave común entre el dataset base y cada fuente adicional. Antes de cada merge, se asegura la conversión del tipo de dato a entero (`src['id'] = src['id'].astype(int)`) para garantizar la coherencia en el cruce.

#### Operación de unión

Se aplica un **LEFT JOIN** (`how='left'`) iterativo sobre el DataFrame base con `pd.merge()`. El LEFT JOIN garantiza que:
- **Ningún registro del dataset base se pierde**, incluso si una fuente no tiene correspondencia.
- Las columnas nuevas se añaden progresivamente al DataFrame acumulado.

```python
# ---- Paso 3: Cruce e integración (merge por id) ----
def enrich(base, sources):
    df = base.copy()
    for name, fmt, src in sources:
        src['id'] = src['id'].astype(int)            # Homogenizar tipo
        df = df.merge(src, on='id', how='left')       # LEFT JOIN
    return df
```

#### Transformaciones aplicadas

| Transformación | Propósito |
|:--|:--|
| `src['id'].astype(int)` | Homogenizar el tipo de la clave de cruce en cada fuente |
| LEFT JOIN secuencial | Preservar todos los registros base sin pérdida de datos |
| Validación de coincidencias | Verificar `notna()` en la primera columna nueva de cada fuente |

**Resultados de la última ejecución:**
<!-- LOG_ENRICH_START -->
```text
✔ Fuente 'departments' (JSON): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['department', 'role']
✔ Fuente 'salaries' (XLSX): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['salary', 'currency']
✔ Fuente 'locations' (CSV): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['city', 'country']
✔ Fuente 'skills' (XML): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['primary_skill', 'level']
✔ Fuente 'projects' (HTML): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['project', 'hours']
✔ Fuente 'notes' (TXT): 10 registros leídos, 10/10 coincidencias, columnas añadidas: ['notes']
```
<!-- LOG_ENRICH_END -->

---

### 4. Exportación de Resultados

#### Dataset Enriquecido (`src/xlsx/enriched_data.xlsx`)

El DataFrame resultante (10 registros × 17 columnas) se exporta a un archivo Excel con `df.to_excel()`, conteniendo la muestra representativa completa del dataset final enriquecido.

| Métrica | Valor |
|:--|:--|
| Registros dataset base | 10 |
| Registros enriquecido | 10 |
| Columnas originales | 6 (`id`, `name`, `username`, `email`, `phone`, `website`) |
| Columnas finales | 17 (6 originales + 11 nuevas) |
| Columnas añadidas | `department`, `role`, `salary`, `currency`, `city`, `country`, `primary_skill`, `level`, `project`, `hours`, `notes` |

Link: https://github.com/CesarPuentes/EA1-Ingesti-n-de-Datos-desde-un-API/blob/main/src/xlsx/enriched_data.xlsx

#### Reporte de Auditoría (`src/static/auditoria/enriched_report.txt`)

Se genera un archivo de log en formato `.txt` que documenta:

- El **número de registros** del dataset base y del enriquecido.
- Las **principales operaciones de cruce**: cantidad de registros coincidentes por fuente y columnas añadidas.
- Los **formatos integrados**, la clave de cruce utilizada y el tipo de join.
- **Observaciones** sobre la integración de cada fuente individual.

```python
# ---- Paso 4b: Reporte de auditoría ----
def report(base, enriched, log):
    txt = f"""
    Registros dataset base : {len(base)}
    Registros enriquecido  : {len(enriched)}
    Columnas originales    : {list(base.columns)}
    Columnas finales       : {list(enriched.columns)}
    Detalle por fuente:
      1. Fuente 'departments' (JSON): ...
      ...
    Formatos integrados: JSON, XLSX, CSV, XML, HTML, TXT
    Clave de cruce: id
    Tipo de join: LEFT JOIN
    """
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(txt)
```

Link: https://github.com/CesarPuentes/EA1-Ingesti-n-de-Datos-desde-un-API/blob/main/src/static/auditoria/enriched_report.txt

---

### 5. Automatización con GitHub Actions

El script de enriquecimiento se ejecuta **después** de los scripts de ingesta (EA1) y limpieza (EA2) dentro del mismo job, asegurando la secuencia correcta del pipeline de datos.

```yaml
# ---- EA3: Ejecución del script de enriquecimiento ----
- name: Ejecutar script de enriquecimiento (EA3)
  run: |
    python src/enrichement.py
    echo "### 📊 Reporte de Auditoría EA3" >> $GITHUB_STEP_SUMMARY
    cat src/static/auditoria/enriched_report.txt >> $GITHUB_STEP_SUMMARY

- name: Subir artefactos EA3 (Dataset Enriquecido y Auditoría)
  uses: actions/upload-artifact@v4
  with:
    name: evidencias-enrichment
    path: |
      src/xlsx/enriched_data.xlsx
      src/static/auditoria/enriched_report.txt
```

El workflow genera evidencias de tres formas:
1. **Logs en consola** — Agrupados con `::group::` / `::endgroup::` para una visualización clara en la interfaz de Actions.
2. **Step Summary** — El reporte de auditoría se imprime directamente en el resumen del paso de GitHub Actions (`$GITHUB_STEP_SUMMARY`).
3. **Artefactos descargables** — `enriched_data.xlsx` y `enriched_report.txt` se suben como `evidencias-enrichment`, descargables desde **Actions → [ejecución reciente] → Artifacts**.

---

## Archivos de Salida

| Archivo | Ruta | Descripción |
|:--|:--|:--|
| Dataset enriquecido | `src/xlsx/enriched_data.xlsx` | DataFrame enriquecido completo (10 × 17) |
| Reporte auditoría | `src/static/auditoria/enriched_report.txt` | Log de todas las operaciones de cruce |

---

## Ejecución Local

> **Prerequisito:** Las EA1 y EA2 deben haberse ejecutado primero para que existan `src/db/ingestion.db` y `src/xlsx/cleaned_data.xlsx`.

```bash
# Paso 1: Ejecutar ingesta (EA1)
python src/ingestion.py

# Paso 2: Ejecutar limpieza (EA2)
python src/cleaning.py

# Paso 3: Ejecutar enriquecimiento (EA3)
python src/enrichement.py
```

---

## Criterios de Evaluación

| Competencia | Evidencia |
|:--|:--|
| **Enriquecimiento en Plataforma Big Data** | `bigdata.yml` ejecuta secuencialmente EA1 → EA2 → EA3 sin errores, generando `evidencias-enrichment` como artefacto descargable desde GitHub Actions. |
| **Calidad del Enriquecimiento** | `enrichement.py` integra correctamente 6 fuentes en formatos distintos (JSON, XLSX, CSV, XML, HTML, TXT) mediante LEFT JOIN, añadiendo 11 columnas con 10/10 coincidencias. |
| **Generación de Evidencias** | `enriched_data.xlsx` con el dataset completo enriquecido y `enriched_report.txt` documentando cada operación de cruce, coincidencias y transformaciones. |
| **Alojamiento y Documentación** | Proyecto en GitHub con estructura requerida. README documenta la trazabilidad completa del pipeline de 3 etapas, instrucciones y workflow. |
