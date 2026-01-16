#!/usr/bin/env python3
"""
Standalone Mercadona product scraper.
Run manually to update products: python scraper_standalone.py
Saves products to data/productos.json
"""
import requests
import json
import os
from pathlib import Path


def scrape_mercadona_products():
    """Scrape all products from Mercadona's API."""
    productos = []
    url = "https://tienda.mercadona.es/api/categories/"

    print("Fetching categories from Mercadona...")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching categories: {response.status_code}")
        return []

    data = response.json()
    total_categories = sum(len(cat['categories']) for cat in data['results'])
    processed = 0

    for categoria in data['results']:
        for subcategoria in categoria['categories']:
            cat_id = str(subcategoria['id'])
            categoria_url = f"https://tienda.mercadona.es/api/categories/{cat_id}/"

            try:
                response = requests.get(categoria_url)
                if response.status_code == 200:
                    cat_data = response.json()
                    for subcat in cat_data['categories']:
                        for product in subcat['products']:
                            productos.append({
                                'id': product['id'],
                                'name': product['slug'],
                                'display_name': product.get('display_name', product['slug']),
                                'category': subcat['name'],
                                'thumbnail': product['thumbnail'],
                                'price': product['price_instructions']['unit_price']
                            })
                else:
                    print(f"Error fetching category {cat_id}: {response.status_code}")
            except Exception as e:
                print(f"Exception fetching category {cat_id}: {e}")

            processed += 1
            print(f"Progress: {processed}/{total_categories} categories processed", end='\r')

    print(f"\nTotal products scraped: {len(productos)}")
    return productos


def save_products(productos, output_path="data/productos.json"):
    """Save products to JSON file."""
    output_file = Path(__file__).parent / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)

    print(f"Products saved to {output_file}")
    return output_file


if __name__ == "__main__":
    productos = scrape_mercadona_products()
    if productos:
        save_products(productos)
    else:
        print("No products scraped. Check your internet connection or the Mercadona API.")
