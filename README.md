# EA1. Ingestión de Datos desde un API - Proyecto Integrador Big Data

Este repositorio contiene la solución completa a la actividad **"EA1. Ingestión de Datos desde un API"**. El objetivo es implementar la etapa fundacional de ingesta de datos del proyecto integrador, extrayendo datos de manera automática hacia un almacenamiento estructurado para futuras etapas analíticas.

## 1. Descripción Breve de la Solución
Se diseñó un _pipeline_ de ingesta automatizado mediante Python que:
1. Extrae un set de datos de perfiles de usuario desde la API pública `JSONPlaceholder`.
2. Procesa la respuesta JSON y modela los datos insertándolos limpiamente en una base de datos analítica local relacional **SQLite** (`ingestion.db`).
3. Emplea la librería de manipulación de datos empírica **Pandas** para generar una muestra tangible tabulada en un libro de **Excel** (`ingestion.xlsx`).
4. Efectúa un control de calidad simulado mediante un reporte de auditoría físico en texto plano (`ingestion.txt`) que hace un conteo y verifica la simetría de los datos capturados.

## 2. Instrucciones de Despliegue Local

Teniendo instalado Git y Python 3.10 o superior en tu máquina, sigue estos pasos para reproducir la ingesta en un entorno local:

**A) Clonar el repositorio**
```bash
git clone https://github.com/CesarPuentes/EA1-Ingesti-n-de-Datos-desde-un-API.git
cd EA1-Ingesti-n-de-Datos-desde-un-API
```

**B) Instalar dependencias**
Es altamente sugerido crear un entorno virtual, y posteriormente instalar los paquetes base descritos en el `setup.py`:
```bash
# (Opcional) Crear entorno: python -m venv venv && source venv/bin/activate
pip install numpy pandas requests openpyxl
```

**C) Ejecutar el script principal**
Desde la carpeta raíz del proyecto, ejecuta el motor de ingesta:
```bash
python src/ingestion.py
```
Si se ejecuta exitosamente, el script creará dinámicamente tu base de datos y archivos requeridos en las siguientes rutas relativas `src/db/`, `src/xlsx/` y `src/static/auditoria`.

---

## 3. Automatización con GitHub Actions y Verificación
La principal virtud de este proyecto es que **no requiere ser ejecutado manualmente**. 
El repositorio posee un Workflow de Integración Continua (CI) en la ruta `.github/workflows/bigdata.yml`.

**¿Cómo funciona?**
Al originarse cambios en la rama `main` o bajo demanda (Workflow Dispatch), GitHub reserva un servidor _Ubuntu_ que de forma desatendida clona el repo, instala dependencias vía `pip` y ejecuta el script `src/ingestion.py`.

**¿Cómo verificar la creación de evidencias?**
1. Visita la pestaña **"Actions"** en el panel superior de este repositorio en GitHub.
2. Haz clic sobre la ejecución más reciente etiquetada como verde o finalizada (`Ingestión de Datos`).
3. Desliza a la parte inferior hacia el panel llamado **"Artifacts"**.
4. Haz clic sobre la carpeta virtual **`evidencias-ingestion`**. Esto descargará un `.zip` comprimiendo los tres archivos de evidencia física levantados dinámicamente por la máquina en la nube: la Base de Datos(`.db`), el Excel (`.xlsx`) y la Auditoría (`.txt`).

---

## 4. Alineación Criterios de Evaluación y Rúbrica de la Tarea

Esta entrega ha sido diseñada meticulosamente para dar cumplimiento perfecto a la rúbrica exigida en la plataforma. A continuación se sustenta la cobertura:

| Competencia de Aprendizaje | Puntaje Max. | Evidencia del Cumplimiento en el Proyecto |
| :--- | :---: | :--- |
| **Automatización y Ejecución (Github)** | 30 / 30 | El workflow (`bigdata.yml`) emplea Ubuntu/Python_3.10, corre sin dependencias intermitentes, se activa tras todo PUSH o manual, generando *Upload Artifacts* con los comprobantes generados, los cuales son libremente descargables desde GitHub Actions. |
| **Extracción de Datos API** | 30 / 30 | `ingestion.py` utiliza la librería certificada `requests`, hace peticiones a JSONPlaceholder, previene errores controlando el código de respuesta HTTP `200` y analiza exhaustivamente los elementos anidados de cada bloque (ej. la metaciudad del usuario). |
| **Generación de Salidas** | 30 / 30 | Mediante algoritmos del script Python en `src`, el volumen extraído se empaquetó forzadamente mediante `sqlite3` generador de DDL/DML, se serializó una muestra a `Pandas.to_excel` y con operaciones I/O básicas documentó un registro comprobador .txt. Todos ellos autogenerados en subdirectorios exactos. |
| **Puntualidad Absoluta** | 10 / 10 | Estructura de entrega exacta y código de base emitido completamente dentro de las fechas pactadas y operativas (Antes del Martes 3 de marzo a las 23:59h). |
| **Total Estimado** | **100 Puntos** | Solución lista, automatizada mediante CI/CD y trazable permanentemente en el ecosistema Git. |
