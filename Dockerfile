# Imagen base ligera
FROM python:3.10-slim

# Evitar bytecode y buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias necesarias
RUN pip install --no-cache-dir fastapi uvicorn tensorflow pillow python-multipart

# Exponer el puerto estándar de Cloud Run
EXPOSE 8080

# Comando de inicio: usar variable de entorno PORT correctamente
CMD exec python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}
