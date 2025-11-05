# =====================================================
# 🌸 API FastAPI - Clasificador de Imágenes (modelo con "no_flor")
# =====================================================
import os
import csv
from io import BytesIO
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image
import numpy as np
import tensorflow as tf

# -----------------------------------------------------
# Configuración inicial
# -----------------------------------------------------
MODEL_PATH = "modelo_flores_no_flor.h5"   # ✅ modelo final entrenado
HISTORIAL_CSV = "historial.csv"

# Silenciar algunas advertencias de TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Cargar el modelo entrenado
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}. Ejecute el entrenamiento primero.")

model = tf.keras.models.load_model(MODEL_PATH)
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Clases del modelo (flores + no_flor)
CLASS_NAMES = ["daisy", "dandelion", "roses", "sunflowers", "tulips", "no_flor"]

# Crear la aplicación FastAPI
app = FastAPI(title="Clasificador de Imágenes - Modelo Flores y No_Flor")

# Permitir acceso desde cualquier origen (útil para conectar con HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear archivo de historial si no existe
if not os.path.exists(HISTORIAL_CSV):
    with open(HISTORIAL_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fecha", "archivo", "categoria", "confianza"])


# -----------------------------------------------------
# Funciones auxiliares
# -----------------------------------------------------
def procesar_imagen_bytes(data: bytes, size=(180, 180)) -> np.ndarray:
    """Convierte bytes de imagen a un arreglo NumPy normalizado listo para el modelo."""
    image = Image.open(BytesIO(data)).convert("RGB")
    image = image.resize(size)
    arr = np.array(image) / 255.0
    arr = np.expand_dims(arr, 0)
    return arr


def guardar_historial(nombre_archivo: str, categoria: str, confianza: float):
    """Guarda cada predicción en un archivo CSV para llevar registro."""
    ahora = datetime.utcnow().isoformat()
    with open(HISTORIAL_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ahora, nombre_archivo, categoria, f"{confianza:.4f}"])


# -----------------------------------------------------
# Endpoints de la API
# -----------------------------------------------------

@app.get("/")
def home():
    """Prueba de conexión básica."""
    return {"mensaje": "API de clasificación activa. Usa /predict para enviar una imagen."}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Recibe una imagen y devuelve la categoría con su nivel de confianza."""
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen válida.")
    try:
        # Procesar imagen
        contenido = await file.read()
        img_array = procesar_imagen_bytes(contenido)

        # Hacer predicción
        preds = model.predict(img_array)
        probs = tf.nn.softmax(preds[0]).numpy()
        idx = int(np.argmax(probs))
        categoria = CLASS_NAMES[idx]
        confianza = float(probs[idx])

        # Nueva lógica: detección de “No flor / objeto desconocido”
        if categoria == "no_flor" or confianza < 0.80:
            categoria = "No flor / objeto desconocido"

        # Guardar en historial
        guardar_historial(file.filename or "sin_nombre", categoria, confianza)

        # Devolver resultado
        return JSONResponse({
            "categoria": categoria,
            "confianza": round(confianza, 4)
        })

    except Exception as e:
        return JSONResponse(
            {"error": "No fue posible procesar la imagen", "detalle": str(e)},
            status_code=500
        )


@app.get("/historial")
def obtener_historial(limit: int = 50):
    """Devuelve las últimas N predicciones registradas."""
    registros = []
    try:
        with open(HISTORIAL_CSV, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            for row in reader[-limit:]:
                registros.append(row)
    except FileNotFoundError:
        pass
    return {"registros": registros}
