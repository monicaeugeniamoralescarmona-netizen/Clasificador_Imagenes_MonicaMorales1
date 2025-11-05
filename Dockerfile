FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn tensorflow pillow python-multipart
EXPOSE 8080
CMD exec python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}
