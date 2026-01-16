"""
JSON-based product search using rapidfuzz for fuzzy matching.
No external dependencies like Elasticsearch required.
"""
import json
from pathlib import Path
from typing import Optional

try:
    from rapidfuzz import fuzz, process
except ImportError:
    raise ImportError("rapidfuzz is required. Install with: pip install rapidfuzz")


# Singleton pattern for product data
_products: Optional[list] = None
_product_names: Optional[list] = None


def load_products(force_reload: bool = False) -> list:
    """Load products from JSON file. Caches in memory for performance."""
    global _products, _product_names

    if _products is not None and not force_reload:
        return _products

    data_file = Path(__file__).parent / "data" / "productos.json"

    if not data_file.exists():
        print(f"Warning: Product data file not found at {data_file}")
        print("Run 'python scraper_standalone.py' to generate product data.")
        _products = []
        _product_names = []
        return _products

    with open(data_file, 'r', encoding='utf-8') as f:
        _products = json.load(f)

    # Pre-compute searchable names for faster lookup
    _product_names = [p['name'].lower().replace('-', ' ') for p in _products]

    print(f"Loaded {len(_products)} products from {data_file}")
    return _products


def _clean_ingredient(ingredient: str) -> str:
    """Clean ingredient string by removing quantities and common words."""
    stopwords = {
        "cucharadas", "cucharada", "cucharadita", "cucharaditas",
        "taza", "tazas", "1/2", "1/4", "1/3", "3/4",
        "pizca", "pizcas", "gramos", "gramo", "kg", "ml", "litro", "litros",
        "unidad", "unidades", "al", "gusto", "de", "la", "el", "los", "las",
        "un", "una", "unos", "unas", "para", "con", "sin", "fresco", "fresca",
        "frescos", "frescas", "grande", "grandes", "pequeno", "pequena",
        "mediano", "mediana", "troceado", "troceada", "picado", "picada",
        "rallado", "rallada", "molido", "molida"
    }

    # Remove numbers and fractions
    words = []
    for word in ingredient.lower().split():
        # Skip if it's a number or fraction
        if word.replace('.', '').replace(',', '').isdigit():
            continue
        if '/' in word and all(p.isdigit() for p in word.split('/')):
            continue
        if word not in stopwords:
            words.append(word)

    return ' '.join(words)


def search_single_product(ingredient: str, threshold: int = 60) -> dict:
    """
    Search for a single product matching the ingredient.

    Args:
        ingredient: The ingredient to search for
        threshold: Minimum fuzzy match score (0-100)

    Returns:
        Best matching product dict or a "not found" placeholder
    """
    products = load_products()

    if not products:
        return {
            'id': '',
            'name': 'NOT FOUND',
            'category': '',
            'thumbnail': '',
            'price': 0
        }

    cleaned = _clean_ingredient(ingredient)
    if not cleaned:
        cleaned = ingredient.lower()

    # Use rapidfuzz to find the best match
    result = process.extractOne(
        cleaned,
        _product_names,
        scorer=fuzz.WRatio,
        score_cutoff=threshold
    )

    if result:
        match_text, score, index = result
        product = _products[index]
        return {
            'id': product['id'],
            'name': product.get('display_name', product['name']).replace('-', ' ').title(),
            'category': product['category'],
            'thumbnail': product['thumbnail'],
            'price': product['price']
        }

    # No match found
    return {
        'id': '',
        'name': f'{ingredient} (no encontrado)',
        'category': '',
        'thumbnail': '',
        'price': 0
    }


def search_products(ingredients: list[str]) -> list[dict]:
    """
    Search for products matching a list of ingredients.

    Args:
        ingredients: List of ingredient strings

    Returns:
        List of product dicts with name, thumbnail (img_url), price, category
    """
    results = []
    seen_ids = set()  # Avoid duplicate products

    for ingredient in ingredients:
        product = search_single_product(ingredient)

        # Avoid duplicates
        if product['id'] and product['id'] in seen_ids:
            continue

        if product['id']:
            seen_ids.add(product['id'])

        # Transform to match frontend expected format
        results.append({
            'name': product['name'],
            'img_url': product['thumbnail'],
            'price': product['price']
        })

    return results


# Pre-load products when module is imported
load_products()


if __name__ == "__main__":
    # Test the search
    test_ingredients = ['huevos', 'aceite de oliva', 'sal', 'pimienta negra', 'espaguetis']
    print("Testing product search...")
    print("-" * 50)

    for ing in test_ingredients:
        result = search_single_product(ing)
        print(f"'{ing}' -> {result['name']} ({result['price']})")

    print("-" * 50)
    print("\nFull search results:")
    results = search_products(test_ingredients)
    for r in results:
        print(f"  - {r['name']}: {r['price']} EUR")
