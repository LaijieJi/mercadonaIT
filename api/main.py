from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from PIL import Image

from food_classifier import FoodImageClassifier
import io

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = FoodImageClassifier()

@app.post("/")
async def analyze_dish(image: UploadFile = File(...)) -> Dict:
    # Leer los bytes de la imagen
    image_bytes = await image.read()
    image = classifier.load_image_from_bytes(image_bytes)
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

    print({"predictions": top_predictions, "clip_similarity": clip_results})

    result = {
        "name": top_predictions,
        "recipe": "",
        "ingredients": "",
        "nutritional_values": ""
    }

    return JSONResponse(content=result)
