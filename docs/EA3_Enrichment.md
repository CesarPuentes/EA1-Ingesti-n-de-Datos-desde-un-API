# EA3 — Enriquecimiento de Datos

## Objetivo

Integrar información complementaria de **6 fuentes en distintos formatos** al dataset limpio generado en EA2, produciendo un dataset enriquecido y un reporte de auditoría.

## Fuentes adicionales

| Archivo | Formato | Columnas añadidas | Ubicación |
|---------|---------|-------------------|-----------|
| `departments.json` | JSON | `department`, `role` | `src/data/` |
| `salaries.xlsx` | XLSX | `salary`, `currency` | `src/data/` |
| `locations.csv` | CSV | `city`, `country` | `src/data/` |
| `skills.xml` | XML | `primary_skill`, `level` | `src/data/` |
| `projects.html` | HTML | `project`, `hours` | `src/data/` |
| `notes.txt` | TXT (pipe) | `notes` | `src/data/` |

## Proceso

1. **Carga del dataset base** — Lee `cleaned_data.xlsx` (salida de EA2)
2. **Lectura de fuentes** — Usa `pd.read_json`, `pd.read_excel`, `pd.read_csv`, `pd.read_xml`, `pd.read_html` y `pd.read_csv(sep='|')` respectivamente
3. **Cruce e integración** — Left join sobre la columna `id` con cada fuente
4. **Exportación** — Genera `enriched_data.xlsx` y `enriched_report.txt`

## Lógica de integración

- **Clave de cruce**: `id` (común a todas las fuentes)
- **Tipo de join**: `LEFT JOIN` — preserva todos los registros del dataset base
- **Transformaciones**: conversión de `id` a entero en cada fuente antes del merge

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

## Artefactos generados

| Artefacto | Ruta | Descripción |
|-----------|------|-------------|
| Dataset enriquecido | `src/xlsx/enriched_data.xlsx` | 10 registros × 17 columnas |
| Reporte de auditoría | `src/static/auditoria/enriched_report.txt` | Detalle de operaciones por fuente |

## Ejecución

```bash
python src/enrichement.py
```

## Automatización

El workflow `bigdata.yml` ejecuta `enrichement.py` después de EA2 y sube los artefactos como `evidencias-enrichment`.
