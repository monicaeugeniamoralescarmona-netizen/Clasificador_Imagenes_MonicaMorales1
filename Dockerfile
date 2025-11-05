# Imagen base oficial de Python
FROM python:3.10

# Crear y establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos del proyecto dentro del contenedor
COPY . /app

# Instalar las dependencias necesarias
RUN pip install tensorflow fastapi uvicorn pillow python-multipart

# Exponer el puerto donde correrá la API
EXPOSE 8000

# Comando que ejecutará el servidor FastAPI al iniciar el contenedor
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "$PORT"]
