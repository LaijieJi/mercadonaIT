import os
# Disable TensorFlow before any imports
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from api import FoodImageClassifier
from api.product_search import search_products


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
    # Read image bytes
    image_bytes = await image.read()
    image = classifier.load_image_from_bytes(image_bytes)

    # Get dish classification and recipe
    top_dish, ingredients, procedure = classifier.classify_and_generate_recipe(image)

    # Search for matching products from Mercadona
    products = []
    if ingredients:
        products = search_products(ingredients)

    # Response matching frontend expected format
    result = {
        "name": top_dish,
        "recipe": procedure,
        "ingredients": products,  # Now contains product info with img_url and price
        "nutritional_values": "",
    }

    return JSONResponse(content=result)
