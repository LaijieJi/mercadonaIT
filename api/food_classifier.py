from transformers import (
    ViTImageProcessor,
    ViTForImageClassification,
    CLIPProcessor,
    CLIPModel,
)
from PIL import Image
import requests
import torch
import io


class FoodImageClassifier:
    def __init__(
        self,
        vit_model_name="nateraw/vit-base-food101",
        clip_model_name="openai/clip-vit-large-patch14",
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
