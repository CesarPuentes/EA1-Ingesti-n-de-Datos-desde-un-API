# Lección: Fundamentos de Ingesta Automatizada de Datos

Para desarrollar exitosamente el proyecto integrador de Big Data, necesitas dominar cuatro pilares tecnológicos. A continuación, exploraremos cada uno de ellos y construiremos las bases para la ingesta.

## 1. Consumo de APIs con `requests`
**¿Qué es?** Las APIs (Interfaces de Programación de Aplicaciones) permiten que dos aplicaciones se comuniquen. En la ingesta de datos, se usan para obtener información de servidores de terceros o repositorios públicos, comúnmente en formato JSON.
**Herramienta:** La librería `requests` de Python.
**Conceptos clave:**
*   **Métodos HTTP:** `GET` (para obtener datos) es el más utilizado en la etapa de ingesta.
*   **Códigos de estado HTTP:** Debes validar que la respuesta sea `200` (OK) antes de procesar la información.
*   **Manejo de JSON:** Convertir la respuesta de texto a diccionarios o listas en Python usando el método `response.json()`.

## 2. Bases de Datos Analíticas con `sqlite3`
**¿Qué es?** SQLite es un motor de base de datos relacional ligero que guarda toda la estructura y registros en un solo archivo (ej. `ingestion.db`). Es ideal para la etapa analítica donde no necesitas un clúster enorme de bases de datos para arrancar.
**Herramienta:** El módulo integrado `sqlite3` de Python.
**Conceptos clave:**
*   **Conexiones:** `sqlite3.connect('mi_base.db')` abre o crea un archivo de base de datos.
*   **Cursores:** Permiten enviar comandos SQL (`cursor.execute()`).
*   **DDL (Data Definition Language):** Sintaxis para crear las tablas (`CREATE TABLE IF NOT EXISTS`).
*   **DML (Data Manipulation Language):** Sintaxis para inyectar datos (`INSERT INTO`). Para muchos datos, conviene usar `cursor.executemany()`.
*   **Transacciones:** Uso de `conn.commit()` para guardar definitivamente los cambios tras los inserts.

## 3. Manipulación de Datos con `pandas`
**¿Qué es?** La librería estándar de la industria en Python para manipulación y análisis de datos tabulares.
**Herramienta:** `pandas` (requiere instalación: `pip install pandas`).
**Conceptos clave:**
*   **DataFrames:** Estructuras de datos bidimensionales (como si fuera una hoja de Excel, pero en código).
*   **Carga de datos:** Crear un DataFrame desde los resultados de una base de datos usando `pd.read_sql_query()`.
*   **Filtrado y Muestreo:** Obtener una muestra representativa de información con métodos como `.head(n)`.
*   **Exportación:** Guardar el DataFrame extraído en un archivo físico para propósitos de evidencia (`df.to_excel()` o `df.to_csv()`).

## 4. Automatización con GitHub Actions
**¿Qué es?** Es el servicio de integración continua (CI) y despliegue continuo (CD) nativo de GitHub. Te permite ejecutar scripts y tareas automáticamente cada vez que ocurre un evento en tu repositorio (por ejemplo, subir código nuevo).

**La mejor forma de entenderlo:**
Imagina que GitHub tiene computadoras en la nube (servidores de Ubuntu, Windows o Mac). Mediante un archivo de configuración, tú le pides a GitHub que preste una de esas computadoras por unos minutos, le instale Python, descargue tu código y presione el botón de "Ejecutar" por ti. 

**Explicación aplicada a tu Proyecto (CesarPuentes/EA1...)**

En tu repositorio de GitHub, la estructura clave para la automatización siempre vivirá en esta ruta oculta:
`.github/workflows/bigdata.yml`

El archivo `bigdata.yml` que creamos antes se lee como una receta de cocina y funciona exactamente así:

1. **El "Trigger" (Cuándo ejecutar):** 
   Le decimos a Github que se active cuando haya un `push` (cuando subas archivos) a la rama `main`, o periódicamente por un *cron* (ej. todos los días a media noche).
   ```yaml
   on:
     push:
       branches: [ "main" ]
   ```

2. **El "Job" y la Computadora (Dónde ejecutar):**
   Le pedimos a Github que cree un entorno limpio, casi siempre usando la última versión de Linux Ubuntu porque es rápido y gratuito.
   ```yaml
   jobs:
     ingestion:
       runs-on: ubuntu-latest
   ```

3. **Los "Steps" (Qué hacer - El paso a paso):**
   - *Checkout:* Le ordena a la máquina de Ubuntu que descargue una copia de todos los archivos de tu repositorio.
   - *Setup Python:* Le decimos que instale internamente la versión 3.10 de Python.
   - *Instalar dependencias:* Usando comandos de terminal, se ejecutan dentro del servidor de Github para instalar `requests`, `pandas`, etc.
   - *Ejecutar Script:* ¡Ahí ocurre la magia! La computadora de GitHub ejecuta literalmente el comando `python src/ingestion.py`. Aquí es donde tu script consume la API y crea la base de datos `ingestion.db`.

4. **El "Artifact" (Obtener la Evidencia):**
   Como la computadora de GitHub se autodestruye al terminar para ahorrar recursos, los archivos `.db`, `.xlsx` o `.txt` que generó tu script se borrarían. 
   Para evitarlo, agregamos un paso final llamado `upload-artifact`. Esto toma los archivos generados y los comprime en un archivo `.zip` que queda guardado en la pestaña "Actions" de tu página de GitHub, listos para que tú (o tu profesor) los descarguen como **"comprobantes" o "evidencias"**.

### Resumen para tu entrega (Repositorio CesarPuentes):
Cuando subas la carpeta y código a tu repositorio `https://github.com/CesarPuentes/EA1-Ingesti-n-de-Datos-desde-un-API`, solo debes dirigirte a la pestaña **"Actions"** (arriba a la izquierda, junto a Pull Requests). Ahí verás tu workflow ejecutándose, un check verde indicará si tu Python corrió sin problemas y abajo a la derecha podrás descargar las evidencias, cumpliendo tu rúbrica.

---

## Desafío Práctico: Micro-Ingesta

Este es un pequeño "ensayo" que simula todo el núcleo de tu tarea. Puedes copiar y pegar todo este bloque en una celda de un **Jupyter Notebook**.

**Objetivo:** Consumir una API pública de usuarios, diseñar una tabla en memoria con SQLite, guardar los usuarios y generar un extracto CSV con Pandas de evidencia.

```python
# 1. Comenta estas dos líneas de abajo si vas a ejecutar en una terminal/entorno donde ya tengas las librerías.
# En Jupyter, si no las tienes, puedes descomentarlas para instalarlas.
# !pip install requests pandas

import requests
import sqlite3
import pandas as pd

# ==========================================
# PASO 1: Extraer datos del API
# ==========================================
url = "https://jsonplaceholder.typicode.com/users" # API pública de prueba
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Se obtuvieron {len(data)} usuarios de la API.")
else:
    print("❌ Error al consumir el API")
    data = []

# ==========================================
# PASO 2: Guardar en SQLite
# ==========================================
# Conectar a una base de datos temporal en memoria (ideal para pruebas repetitivas)
conn = sqlite3.connect(':memory:') # En tu proyecto usarás 'ingestion.db'
cursor = conn.cursor()

# Crear estructura
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        email TEXT,
        ciudad TEXT
    )
''')

# Extraer campos clave del JSON para insertar
# Nota: exploramos el diccionario del JSON porque 'ciudad' viene anidado en 'address'
datos_insertar = [(user['id'], user['name'], user['email'], user['address']['city']) for user in data]

# Insertar el lote de datos
cursor.executemany('INSERT INTO usuarios (id, nombre, email, ciudad) VALUES (?, ?, ?, ?)', datos_insertar)
conn.commit()
print("✅ Datos guardados y confirmados en SQLite.")

# ==========================================
# PASO 3: Generar muestra y auditoría con Pandas
# ==========================================
# Extraer la información desde la base de datos local al DataFrame
query = "SELECT * FROM usuarios"
df_sqlite = pd.read_sql_query(query, conn)

# Auditoría de integridad simulada
registros_api = len(data)
registros_bd = len(df_sqlite)

print(f"\\n--- REPORTE DE AUDITORÍA ---")
print(f"Volumen recibido del API: {registros_api}")
print(f"Volumen extraído de la BD: {registros_bd}")
print(f"¿Integridad correcta?: {'Sí' if registros_api == registros_bd else 'No'}")

# Crear la muestra física (evidencia)
df_sqlite.to_csv('muestra_ingesta_usuarios.csv', index=False)
print("\\n✅ Archivo 'muestra_ingesta_usuarios.csv' generado correctamente.")

# Cierre de conexión
conn.close()

# Mostrar un adelanto de la información en Jupyter
df_sqlite.head(3)
```
