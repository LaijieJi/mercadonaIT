from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Dict
from PIL import Image

from food_classifier import FoodImageClassifier
import io

app = FastAPI()
classifier = FoodImageClassifier()

@app.post("/")
async def analyze_dish(image: UploadFile = File(...)) -> Dict:
    # Read the image file
    image = classifier.load_image(await image.read())
    print("Image size:", len(image), "Bytes")

    # Clasificar la imagen (ViT)
    top_predictions = classifier.classify_food(image, top_k=3)

    print("Predicciones de comida:")
    for label, score in top_predictions:
        print(f"{label}: {score:.2%}")

    # (Opcional) Evaluar similitud con CLIP usando los textos de predicción
    texts = [label for label, _ in top_predictions]
    clip_results = classifier.get_clip_similarity(image, texts)

    print("\nSimilitud CLIP:")
    for text, score in clip_results:
        print(f"{text}: {score:.2%}")

    # Dummy output
    # result = {
    #     "dish_name": "Tortilla Española",
    #     "ingredients": [
    #         "4 eggs",
    #         "3 potatoes",
    #         "1 onion",
    #         "olive oil",
    #         "salt"
    #     ],
    #     "nutritional_value": {
    #         "calories": "200 kcal",
    #         "protein": "7g",
    #         "carbohydrates": "15g",
    #         "fat": "12g"
    #     },
    #     "recipe": [
    #         "Peel and slice potatoes and onion.",
    #         "Fry in olive oil until soft.",
    #         "Beat the eggs and mix with fried mixture.",
    #         "Cook in a pan until set on both sides."
    #     ]
    # }

    return JSONResponse(content=result)
