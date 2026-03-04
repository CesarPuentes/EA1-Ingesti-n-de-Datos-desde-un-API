from setuptools import setup, find_packages

setup(
    name='ingestion_api',
    version='0.1.0',
    description='Proyecto integrador de Ingesta de Datos para la EA1',
    author='Estudiante Asignado',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'openpyxl'
    ],
)
