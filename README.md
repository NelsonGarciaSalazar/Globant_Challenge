# Globant Data Engineering Challenge

Este proyecto implementa una solución completa en Flask para carga, consulta y análisis de datos relacionados con contrataciones, usando Azure Blob Storage, Azure SQL y Docker.

## Requisitos

- Python 3.11+
- Docker
- Cuenta en Azure con:
  - Azure SQL Database
  - Azure Blob Storage

## Estructura del proyecto
app/

api/ # Endpoints REST

core/ # Lógica de negocio

domain/ # Modelos de dominio

infra/ # Adaptadores: base de datos y blob

main.py # Entrada principal de Flask

config.py # Variables de entorno

## Instalación

1. Clonar el repositorio
2. Crear un archivo `.env` con:

    AZURE_STORAGE_CONNECTION_STRING=...

    AZURE_STORAGE_CONTAINER=...

    AZURE_SQL_CONNECTION_STRING=...

3. Instalar dependencias
pip install -r requirements.txt

## Docker
docker build -t globant-challenge .

Ejecutar contenedor

docker run -p 5000:5000 --env-file .env globant-challenge

## Endpoints
