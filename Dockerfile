# Imagen base
FROM python:3.10

# Evita que Python guarde bytecode y use buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Google Cloud Run define la variable $PORT automáticamente
ENV PORT=8080

# Directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir fastapi uvicorn tensorflow pillow python-multipart

# Exponer el puerto (solo informativo)
EXPOSE 8080

# Comando de ejecución: usa el puerto que Cloud Run le asigne
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT}
