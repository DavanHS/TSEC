#!/usr/bin/env python3
"""
Fetch ALL products from all categories in dummyjson.com API
"""
import json
import os
import requests
from pathlib import Path

API_BASE = "https://dummyjson.com/products"
DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"

# Get all categories
def get_categories():
    response = requests.get(f"{API_BASE}/categories")
    return response.json()

def fetch_products_by_category(category_slug, limit=100):
    """Fetch products from a specific category"""
    response = requests.get(f"{API_BASE}/category/{category_slug}?limit={limit}")
    if response.status_code == 200:
        return response.json().get("products", [])
    return []

def transform_product(p, global_index):
    """Transform dummyjson product to our format"""
    category = p.get("category", "Unknown")
    brand = p.get("brand", "Unknown")
    
    # Create features from available data
    features = []
    if p.get("warrantyInformation"):
        features.append(p["warrantyInformation"])
    if p.get("shippingInformation"):
        features.append(p["shippingInformation"])
    if p.get("availabilityStatus"):
        features.append(p["availabilityStatus"])
    
    return {
        "id": f"prod_{global_index:04d}",
        "name": p.get("title", ""),
        "description": p.get("description", ""),
        "category": f"Electronics > {category.capitalize()}",
        "brand": brand,
        "price": float(p.get("price", 0) * 75),  # Convert to INR
        "rating": float(p.get("rating", 0)),
        "features": features[:5],
        "image_path": None,
        "thumbnail": p.get("thumbnail", ""),
        "images": p.get("images", [])
    }

def download_image(img_url, filepath):
    """Download a single image"""
    if not img_url or os.path.exists(filepath):
        return False
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Failed: {e}")
    return False

def main():
    print("=== Fetching ALL Products from dummyjson.com ===\n")
    
    # Get categories
    categories = get_categories()
    print(f"Found {len(categories)} categories")
    
    all_products = []
    global_index = 0
    
    for cat in categories:
        slug = cat["slug"]
        name = cat["name"]
        print(f"Fetching {name}...", end=" ")
        
        products = fetch_products_by_category(slug)
        print(f"{len(products)} products")
        
        for p in products:
            transformed = transform_product(p, global_index)
            all_products.append(transformed)
            global_index += 1
    
    print(f"\n=== Total: {len(all_products)} products ===")
    
    # Download images for first 50 products
    print("\n=== Downloading Product Images ===")
    IMAGES_DIR.mkdir(exist_ok=True)
    
    for i, product in enumerate(all_products[:50]):
        images = product.get("images", [])
        if not images:
            continue
        
        img_url = images[0]
        if img_url:
            ext = os.path.splitext(img_url.split('?')[0])[-1] or '.jpg'
            filename = f"product_{i:04d}{ext}"
            filepath = IMAGES_DIR / filename
            
            if download_image(img_url, filepath):
                product['image_path'] = str(filepath)
                print(f"Saved: {filename}")
    
    # Clean up - remove images array to save space
    for p in all_products:
        if "images" in p:
            del p["images"]
    
    # Save to products.json
    output_path = DATA_DIR / "products.json"
    with open(output_path, "w") as f:
        json.dump(all_products, f, indent=2)
    
    print(f"\n=== Saved {len(all_products)} products to {output_path} ===")
    
    # Summary
    cats = {}
    for p in all_products:
        cat = p["category"].split(" > ")[-1]
        cats[cat] = cats.get(cat, 0) + 1
    
    print("\nCategories:")
    for k, v in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()