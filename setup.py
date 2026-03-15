from setuptools import setup, find_packages

setup(
    name='ingestion_api',
    version='0.1.0',
    description='Proyecto integrador Big Data - EA1 Ingesta y EA2 Preprocesamiento',
    author='Estudiante Asignado',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'openpyxl'
    ],
)
