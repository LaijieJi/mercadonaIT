from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Dict
from PIL import Image

from .food_classifier import FoodImageClassifier
import io

app = FastAPI()

@app.post("/")
async def analyze_dish(image: UploadFile = File(...)) -> Dict:
    # Read the image file
    contents = await image.read()
    image_pil = Image.open(io.BytesIO(contents))
    print("Image size:", len(contents), "Bytes")

    # TODO: Process image with ML model or external API

    # Dummy output
    result = {
        "dish_name": "Tortilla Española",
        "ingredients": [
            "4 eggs",
            "3 potatoes",
            "1 onion",
            "olive oil",
            "salt"
        ],
        "nutritional_value": {
            "calories": "200 kcal",
            "protein": "7g",
            "carbohydrates": "15g",
            "fat": "12g"
        },
        "recipe": [
            "Peel and slice potatoes and onion.",
            "Fry in olive oil until soft.",
            "Beat the eggs and mix with fried mixture.",
            "Cook in a pan until set on both sides."
        ]
    }

    return JSONResponse(content=result)
