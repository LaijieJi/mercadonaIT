from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from PIL import Image

from api import FoodImageClassifier


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

    # Obtener el plato más probable usando la nueva función
    top_dish, ingredients, procedure = classifier.classify_and_generate_recipe(image)

    # Respuesta
    result = {
        "name": top_dish,
        "recipe": procedure,
        "ingredients": ingredients,
        "nutritional_values": "",
    }

    return JSONResponse(content=result)
