from transformers import (
    ViTImageProcessor,
    ViTForImageClassification,
    CLIPProcessor,
    CLIPModel,
)
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from PIL import Image
import requests
import torch
import io
from googletrans import Translator
import asyncio
import deepl


class FoodImageClassifier:
    def __init__(
        self,
        vit_model_name="nateraw/vit-base-food101",
        clip_model_name="openai/clip-vit-large-patch14",
        recipe_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    ):
        # Load ViT model and processor for food classification
        self.vit_model = ViTForImageClassification.from_pretrained(vit_model_name)
        self.vit_processor = ViTImageProcessor.from_pretrained(vit_model_name)

        # Load CLIP model and processor for image-text similarity
        self.clip_model = CLIPModel.from_pretrained(clip_model_name)
        self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)

        # Move models to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vit_model.to(self.device)
        self.clip_model.to(self.device)
        self.recipe_model_name = recipe_model_name
        self.recipe_generator = None

    def load_image_from_bytes(self, image_bytes: bytes) -> Image.Image:
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def load_image(self, contents) -> Image.Image:
        return Image.open(io.BytesIO(contents)).convert("RGB")

    def classify_food(self, image: Image.Image, top_k: int = 3):
        inputs = self.vit_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.vit_model(**inputs)
        logits = outputs.logits
        probs = logits.softmax(dim=-1)
        topk = torch.topk(probs, k=top_k)

        labels = [
            self.vit_model.config.id2label[idx.item()].replace("_", " ").title()
            for idx in topk.indices[0]
        ]
        scores = [round(prob.item(), 4) for prob in topk.values[0]]

        return list(zip(labels, scores))

    def get_clip_similarity(self, image: Image.Image, candidate_texts: list):
        inputs = self.clip_processor(
            text=candidate_texts, images=image, return_tensors="pt", padding=True
        ).to(self.device)
        with torch.no_grad():
            outputs = self.clip_model(**inputs)

        logits_per_image = outputs.logits_per_image  # shape: [1, len(candidate_texts)]
        probs = logits_per_image.softmax(dim=1)  # Normalize to probabilities
        return list(zip(candidate_texts, probs[0].tolist()))

    def predict_top_dish(self, image: Image.Image) -> str:
        top_prediction = self.classify_food(image, top_k=1)[0]
        label, score = top_prediction
        return label

    def generate_recipe(self, dish_name: str) -> str:
        if self.recipe_generator is None:
            self.recipe_generator = pipeline(
                "text-generation",
                model=self.recipe_model_name,
                device=torch.device(
                    "mps" if torch.backends.mps.is_available() else "cpu"
                ),
            )

        prompt = f"<|im_start|>user\nGenerate a recipe for {dish_name}, give first the list of ingredients following an ordered list. Then, add two line jumps and the procedure step by step using also an ordered list.|im_end|>\n<|im_start|>assistant\n"
        recipe = self.recipe_generator(prompt, num_return_sequences=1)[0][
            "generated_text"
        ]
        recipe = recipe.split("assistant\n")[1].strip()
        ingredients = (
            recipe.split("\n\n")[0].split("Ingredients:\n-")[1].strip().split("\n-")
        )
        procedure = recipe.split("Procedure:\n")[1].strip().split("\n\n")[0].split("\n")
        return ingredients, procedure

    def translate(self, prompt):
        auth_key = "DEEPL_TOKEN"
        trans = deepl.Translator(auth_key)
        result = trans.translate_text(prompt, target_lang="ES")
        return result.text

    def classify_and_generate_recipe(self, image: Image.Image) -> tuple:
        """Clasifica la imagen y genera una receta para el plato."""
        dish_name = self.predict_top_dish(image)
        ingredients, procedure = self.generate_recipe(dish_name)
        ingredients = [self.translate(ingredient) for ingredient in ingredients]
        procedure = [self.translate(step) for step in procedure]
        return dish_name, ingredients, procedure
