# Proyecto Integrador Big Data – EA1 + EA2

Repositorio del proyecto integrador de **Infraestructura y Arquitectura para Big Data**.

## Proceso completo

```mermaid
flowchart TD
    A([🌐 API JSONPlaceholder\n/users]) --> B

    subgraph EA1["EA1 — ingestion.py"]
        B[Extracción con requests] --> C[Almacenamiento en SQLite\ningestion.db]
        C --> D[Muestra Excel\ningestion.xlsx]
        C --> E[Auditoría de integridad\ningestion.txt]
    end

    subgraph EA2["EA2 — cleaning.py"]
        C --> F[Carga desde BD\nsimulación cloud]
        F --> G[Análisis Exploratorio\nduplicados · nulos · tipos]
        G --> H[Limpieza y Transformación\ndedup · imputación · normalización]
        H --> I[Datos limpios\ncleaned_data.xlsx]
        H --> J[Reporte de auditoría\ncleaning_report.txt]
    end

    subgraph GH["GitHub Actions — bigdata.yml"]
        direction LR
        K([push / cron]) --> L[Ejecuta EA1] --> M[Ejecuta EA2] --> N[📦 Artefactos descargables]
    end
```



## Actividades

| Actividad | Descripción | Script | Documentación detallada |
|:--|:--|:--|:--|
| **EA1** | Ingestión de Datos desde un API | `src/ingestion.py` | [📄 EA1\_Ingestion.md](docs/EA1_Ingestion.md) |
| **EA2** | Preprocesamiento y Limpieza de Datos | `src/cleaning.py` | [📄 EA2\_Cleaning.md](docs/EA2_Cleaning.md) |

---

## Pipeline general

```
API (JSONPlaceholder /users)
       ↓  EA1 — ingestion.py
  SQLite DB  →  ingestion.xlsx  →  ingestion.txt
       ↓  EA2 — cleaning.py
 DataFrame limpio  →  cleaned_data.xlsx  →  cleaning_report.txt
```

![git1](git1.png)
![git2](git2.png)
![git3](git3.png)

---

## Ejecución local

```bash
# Instalar dependencias
pip install requests pandas openpyxl

# EA1: Ingesta de datos
python src/ingestion.py

# EA2: Preprocesamiento y limpieza
python src/cleaning.py
```

---

## GitHub Actions

El workflow `.github/workflows/bigdata.yml` ejecuta ambas etapas automáticamente en cada `push` a `main`, por cron diario y manualmente desde la interfaz de GitHub.

Los artefactos son descargables desde **Actions → [ejecución reciente] → Artifacts**:
- **`evidencias-ingestion`** — `ingestion.db`, `ingestion.xlsx`, `ingestion.txt`
- **`evidencias-cleaning`** — `cleaned_data.xlsx`, `cleaning_report.txt`

---

## Estructura del proyecto

```
├── README.md
├── docs/
│   ├── EA1_Ingestion.md
│   └── EA2_Cleaning.md
├── .github/workflows/bigdata.yml
├── setup.py
└── src/
    ├── ingestion.py
    ├── cleaning.py
    ├── db/ingestion.db
    ├── xlsx/
    │   ├── ingestion.xlsx
    │   └── cleaned_data.xlsx
    └── static/auditoria/
        ├── ingestion.txt
        └── cleaning_report.txt
```
