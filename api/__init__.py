import os
# Disable TensorFlow before any imports
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"

from .food_classifier import FoodImageClassifier
from .product_search import search_products

__all__ = ['FoodImageClassifier', 'search_products']
