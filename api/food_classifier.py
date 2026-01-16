import os
# Disable TensorFlow before importing transformers
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"

import re
import logging
from transformers import (
    ViTImageProcessor,
    ViTForImageClassification,
)
from transformers import pipeline
from PIL import Image
import torch
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FoodImageClassifier:
    def __init__(
        self,
        vit_model_name="nateraw/vit-base-food101",
        recipe_model_name="Qwen/Qwen2.5-1.5B-Instruct",
    ):
        # Load ViT model and processor for food classification
        self.vit_model = ViTForImageClassification.from_pretrained(vit_model_name)
        self.vit_processor = ViTImageProcessor.from_pretrained(vit_model_name)

        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vit_model.to(self.device)

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

    def predict_top_dish(self, image: Image.Image) -> str:
        top_prediction = self.classify_food(image, top_k=1)[0]
        label, score = top_prediction
        return label

    def generate_recipe(self, dish_name: str) -> tuple[list[str], list[str]]:
        """Generate a recipe in Spanish for the given dish."""
        logger.info(f"=== GENERATING RECIPE FOR: {dish_name} ===")

        if self.recipe_generator is None:
            logger.info(f"Loading recipe model: {self.recipe_model_name}")
            self.recipe_generator = pipeline(
                "text-generation",
                model=self.recipe_model_name,
                device=torch.device(
                    "mps" if torch.backends.mps.is_available() else "cpu"
                ),
            )

        # Qwen ChatML format
        prompt = f"""<|im_start|>system
You are a helpful cooking assistant. Always respond in Spanish with accurate recipes.<|im_end|>
<|im_start|>user
Escribe una receta para {dish_name}.

Usa exactamente este formato:

Ingredientes:
- ingrediente con cantidad
- ingrediente con cantidad
- ingrediente con cantidad

Pasos:
1. Primer paso detallado
2. Segundo paso detallado
3. Tercer paso detallado

Solo escribe la receta, nada más.<|im_end|>
<|im_start|>assistant
"""

        try:
            logger.info("Calling recipe generator...")
            result = self.recipe_generator(
                prompt,
                max_new_tokens=512,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.recipe_generator.tokenizer.eos_token_id
            )
            recipe_text = result[0]["generated_text"]

            logger.info(f"=== RAW MODEL OUTPUT ===\n{recipe_text}\n=== END RAW OUTPUT ===")

            # Extract only the assistant's response (handle different formats)
            if "<|im_start|>assistant" in recipe_text:
                recipe_text = recipe_text.split("<|im_start|>assistant")[-1].strip()
            elif "<|assistant|>" in recipe_text:
                recipe_text = recipe_text.split("<|assistant|>")[-1].strip()
            elif "assistant" in recipe_text:
                recipe_text = recipe_text.split("assistant")[-1].strip()

            # Remove any end tokens
            recipe_text = recipe_text.replace("<|im_end|>", "").replace("<|end|>", "").strip()

            logger.info(f"=== EXTRACTED ASSISTANT RESPONSE ===\n{recipe_text}\n=== END EXTRACTED ===")

            return self._parse_recipe_output(recipe_text)

        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return [], []

    def _parse_recipe_output(self, recipe_text: str) -> tuple[list[str], list[str]]:
        """
        Parse recipe output with robust error handling.
        Returns (ingredients, procedure) lists, or empty lists on failure.
        """
        logger.info("=== PARSING RECIPE OUTPUT ===")
        ingredients = []
        procedure = []

        try:
            # Normalize text
            text = recipe_text.strip()

            # Try multiple patterns for ingredients section
            ingredients_patterns = [
                r'[Ii]ngredientes?:?\s*\n((?:[-*]\s*.+\n?)+)',
                r'[Ii]ngredients?:?\s*\n((?:[-*]\s*.+\n?)+)',
                r'[Ii]ngredientes?:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
            ]

            for pattern in ingredients_patterns:
                match = re.search(pattern, text)
                if match:
                    ing_text = match.group(1)
                    # Extract individual ingredients
                    ing_lines = re.findall(r'[-*]\s*(.+)', ing_text)
                    if not ing_lines:
                        ing_lines = re.findall(r'\d+[.)]\s*(.+)', ing_text)
                    if ing_lines:
                        ingredients = [line.strip() for line in ing_lines if line.strip()]
                        break

            # Fallback: look for lines starting with dash after "Ingredientes"
            if not ingredients:
                if 'ngrediente' in text.lower():
                    parts = re.split(r'[Ii]ngredientes?:?', text, maxsplit=1)
                    if len(parts) > 1:
                        rest = parts[1]
                        # Take lines until we hit "Pasos" or "Procedimiento"
                        rest = re.split(r'[Pp]asos?|[Pp]rocedimiento|[Pp]reparacion', rest)[0]
                        for line in rest.split('\n'):
                            line = line.strip()
                            if line.startswith('-') or line.startswith('*'):
                                ingredients.append(line.lstrip('-* ').strip())
                            elif re.match(r'^\d+[.)]\s*', line):
                                ingredients.append(re.sub(r'^\d+[.)]\s*', '', line).strip())

            # Try multiple patterns for procedure/steps section
            procedure_patterns = [
                r'[Pp]asos?:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
                r'[Pp]rocedimiento:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
                r'[Pp]reparacion:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
                r'[Pp]rocedure:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
                r'[Ss]teps?:?\s*\n((?:\d+[.)]\s*.+\n?)+)',
            ]

            for pattern in procedure_patterns:
                match = re.search(pattern, text)
                if match:
                    proc_text = match.group(1)
                    proc_lines = re.findall(r'\d+[.)]\s*(.+)', proc_text)
                    if proc_lines:
                        procedure = [line.strip() for line in proc_lines if line.strip()]
                        break

            # Fallback: look for numbered lines after "Pasos"
            if not procedure:
                step_markers = ['pasos', 'procedimiento', 'preparacion', 'procedure', 'steps']
                for marker in step_markers:
                    if marker in text.lower():
                        parts = re.split(rf'[{marker[0].upper()}{marker[0]}]{marker[1:]}:?', text, maxsplit=1)
                        if len(parts) > 1:
                            rest = parts[1]
                            for line in rest.split('\n'):
                                line = line.strip()
                                if re.match(r'^\d+[.)]\s*', line):
                                    step = re.sub(r'^\d+[.)]\s*', '', line).strip()
                                    if step:
                                        procedure.append(step)
                            if procedure:
                                break

        except Exception as e:
            logger.error(f"Error parsing recipe: {e}")

        # Clean up results
        ingredients = [ing for ing in ingredients if ing and len(ing) > 1]
        procedure = [step for step in procedure if step and len(step) > 1]

        logger.info(f"=== PARSED INGREDIENTS ({len(ingredients)}) ===")
        for i, ing in enumerate(ingredients):
            logger.info(f"  {i+1}. {ing}")
        logger.info(f"=== PARSED STEPS ({len(procedure)}) ===")
        for i, step in enumerate(procedure):
            logger.info(f"  {i+1}. {step}")

        return ingredients, procedure

    def classify_and_generate_recipe(self, image: Image.Image) -> tuple[str, list[str], list[str]]:
        """Classify the image and generate a recipe for the dish."""
        logger.info("=== STARTING CLASSIFICATION AND RECIPE GENERATION ===")
        dish_name = self.predict_top_dish(image)
        logger.info(f"Classified dish: {dish_name}")
        ingredients, procedure = self.generate_recipe(dish_name)
        logger.info(f"=== FINAL RESULT: {dish_name} with {len(ingredients)} ingredients and {len(procedure)} steps ===")
        return dish_name, ingredients, procedure
