# Guía Definitiva de GitHub Actions y Automatización para Big Data

Esta guía explica conceptualmente qué es GitHub Actions y detalla, línea por línea, cómo funciona el archivo de automatización (`bigdata.yml`) programado para la Tarea de Ingestión de Datos.

---

## 1. El Concepto Teórico: ¿Qué es GitHub Actions?

Para entender GitHub Actions, resulta más fácil compararlo con un **asistente virtual en la nube**.

Cuando tú codificas en tu computadora, usas recursos físicos locales: tu teclado, la memoria RAM de tu máquina, y tu propio Python instalado. GitHub Actions es el equivalente a **pedirle prestada una computadora limpia a GitHub** durante 2 o 3 minutos para que corra tus scripts o programas.

En el ciclo de "Integración Continua (CI)", esto brinda una ventaja clave a los desarrolladores y a los ingenieros de Big Data:
No importa si estás en Windows, Mac o Linux, o si se te olvidó instalar una dependencia localmente. Al configurar GitHub Actions, te aseguras de que en un "ambiente estéril" (un servidor nuevo en la nube que se destruye tras usarse), tu código sea válido, logre ejecutarse y brinde los resultados esperados.

### ¿A qué le llamamos "Workflow"?
Un **Workflow** (Flujo de Trabajo) es como una receta de cocina que tu proyecto de código le entrega a ese asistente (GitHub Actions). Esta receta (un archivo que siempre termina en `.yml`), tiene tres preguntas intrínsecas que debe contestar:
1. **¿Cuándo quiero que se ejecute el código?** (El evento disparador).
2. **¿Qué computadora necesito?** (El entorno; por ejemplo, Ubuntu o Windows).
3. **¿Cuáles son los pasos?** (Abre la terminal, instala la librería `requests`, luego escribe `python mi_codigo.py`, etc).

---

## 2. Radiografía paso a paso del archivo `bigdata.yml`

A continuación, analizamos cada bloque de la receta que usamos en la etapa de ingesta.

```yaml
name: Ingestión de Datos
```
Este es el "bautizo" de tu receta. Sirve para que, cuando entres a la pestaña "Actions" en tu cuenta de GitHub, puedas ver un botón con este nombre que identifique claramente tu proyecto.

```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * *' # Ejecutar diariamente a la medianoche
  workflow_dispatch: # Permitir ejecución manual desde la interfaz de GitHub
```
El bloque **`on:`** es el evento disparador o _"trigger"_. Aquí estamos dándole explícitamente **4 alternativas diferentes** para arrancar el proceso de la Ingesta de Datos:
* **push**: Se ejecutará automáticamente cada vez que alguien escriba un commit y suba nuevas líneas de código a la rama `main` (rama principal).
* **pull_request**: Si alguien sugiere un cambio de código y pide integrarlo, correrá primero.
* **schedule (cron)**: En el mundo del Big Data, las ventanas de ingesta (ETL/ELT) suelen darse mediante "procesos batch" en la madrugada (cuando menos usuarios cargan bases de datos transaccionales). El código `'0 0 * * *'` le dice a GitHub que asigne su computadora de forma desatendida a las 12:00 de la noche y descargue los datos.
* **workflow_dispatch**: Añade un botoncito de "Play" a la interfaz de GitHub, que permite correr el script de forma manual en el momento que tú prefieras probar.

```yaml
jobs:
  ingestion:
    runs-on: ubuntu-latest
```
Un _job_ equivale a una computadora. Aquí le estamos diciendo a GitHub: "Préstame una máquina (servidor) virtual que corra la última versión estable del sistema operativo Ubuntu (Linux)". 

```yaml
    steps:
    - name: Checkout del repositorio
      uses: actions/checkout@v4
```
Empezamos con los pasos. Esta computadora de Ubuntu "nace" completamente vacía. La acción oficial llamada **Checkout** clona absolutamente todos los archivos y carpetas (.py, .md) que están alojados en tu repositorio remoto y los copia dentro del disco duro virtual temporal de la máquina de Ubuntu. 

```yaml
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
```
Instalamos Python. A diferencia de tu ordenador, donde demoras descargando de python.org, GitHub instala fluidamente las bases de la versión estándar 3.10 en el hilo de trabajo de acciones.

```yaml
    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install requests pandas openpyxl
```
Con la etiqueta `run`, escribimos comandos directos a la consola/terminal de Ubuntu (`bash`). Actualizamos el empaquetador de módulos y descargamos de la nube las librerías necesarias:
* `requests`: para el protocolo web hacia la API.
* `pandas` y `openpyxl`: para trabajar tablas matemáticas y exportarlas a Excel (.xlsx).

```yaml
    - name: Ejecutar script de ingesta
      run: |
        python src/ingestion.py
```
**¡Este es el clímax de tu tarea!**
Es la ejecución. El servidor virtual llama a tu _script_ de Python alojado en la ruta `src/ingestion.py`. Aquí, el procesador empezará a ejecutar e instruirá a SQLite a que guarde bases de datos basándose en el consumo del API (`JSONPlaceholder`).
Al llegar a la última capa del diseño, se habrán generado dentro de la máquina archivos físicos.

```yaml
    - name: Subir artefactos generados (Base de Datos, Muestra y Auditoría)
      uses: actions/upload-artifact@v4
      with:
        name: evidencias-ingestion
        path: |
          src/db/ingestion.db
          src/xlsx/ingestion.xlsx
          src/static/auditoria/ingestion.txt
```
**Artefactos (Cosechar y Guardar).**
Recuerda que, una vez que termine, **la computadora de GitHub se autodestruye** llevándose consigo a todos los excels (.xlsx) o bases de datos (.db) extraídas en la memoria virtual si no los salvamos.

Este último paso (`upload-artifact`) envuelve a la respuesta y a las evidencias, las comprime en un objeto, y "las cuelga" temporalmente en la página web de Actions bajo el nombre de `evidencias-ingestion` para que tu usuario final (o profesor) pueda evaluarlas y ver que verdaderamente la canalización ocurrió de principio a fin.
