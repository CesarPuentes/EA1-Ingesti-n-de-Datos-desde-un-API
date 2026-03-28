from setuptools import setup, find_packages

setup(
    name='ingestion_api',
    version='0.3.0',
    description='Proyecto integrador Big Data - EA1 Ingesta, EA2 Preprocesamiento y EA3 Enriquecimiento',
    author='Estudiante Asignado',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'openpyxl',
        'lxml',
    ],
)
