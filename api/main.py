from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Dict
from PIL import Image

from .food_classifier import FoodImageClassifier
import io

app = FastAPI()
classifier = FoodImageClassifier()


# Nuevo método para leer imágenes desde bytes
def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


@app.post("/")
async def analyze_dish(image: UploadFile = File(...)) -> Dict:
    # Leer los bytes de la imagen
    image_bytes = await image.read()
    image = load_image_from_bytes(image_bytes)
    print("Image size:", image.size)

    # Clasificar la imagen (ViT)
    top_predictions = classifier.classify_food(image, top_k=3)

    print("Predicciones de comida:")
    for label, score in top_predictions:
        print(f"{label}: {score:.2%}")

    # Evaluar similitud con CLIP usando los textos de predicción
    texts = [label for label, _ in top_predictions]
    clip_results = classifier.get_clip_similarity(image, texts)

    print("\nSimilitud CLIP:")
    for text, score in clip_results:
        print(f"{text}: {score:.2%}")

    return JSONResponse(
        content={"predictions": top_predictions, "clip_similarity": clip_results}
    )
