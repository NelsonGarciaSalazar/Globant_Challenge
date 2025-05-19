# Imagen base oficial de Python compatible con ODBC y Azure
FROM python:3.11-slim-bullseye

# Evita prompts de configuración al instalar paquetes
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        apt-transport-https \
        ca-certificates \
        unixodbc-dev \
        && \
    # Importa la clave del repositorio de Microsoft
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    # Instala msodbcsql18
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copia y configura dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia el resto de tu proyecto
COPY . .

# 5. Variables de entorno (puedes sobreescribir con `docker run -e`)
ENV FLASK_APP=main.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=production

# 6. Exponer el puerto
EXPOSE 80

# 7. Ejecutar la aplicación Flask con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]
