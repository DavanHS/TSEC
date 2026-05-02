#!/usr/bin/env python3
import json
import os
import requests
from urllib.parse import urlparse
import time

DATA_DIR = "/root/projects/TSEC/data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

os.makedirs(IMAGES_DIR, exist_ok=True)

with open(PRODUCTS_FILE, "r") as f:
    products = json.load(f)

print(f"Found {len(products)} products")
print(f"Current images: {len(os.listdir(IMAGES_DIR))}")

for i, product in enumerate(products):
    prod_id = product["id"]
    thumbnail_url = product.get("thumbnail")
    
    if not thumbnail_url:
        print(f"Skip {prod_id}: no thumbnail")
        continue
    
    local_path = os.path.join(IMAGES_DIR, f"{prod_id}.webp")
    
    if os.path.exists(local_path):
        print(f"Skip {prod_id}: already exists")
        continue
    
    try:
        print(f"Downloading {prod_id}: {thumbnail_url[:60]}...")
        response = requests.get(thumbnail_url, timeout=30)
        response.raise_for_status()
        
        with open(local_path, "wb") as f:
            f.write(response.content)
        
        print(f"Saved: {local_path} ({len(response.content)} bytes)")
        time.sleep(0.2)
        
    except Exception as e:
        print(f"Error {prod_id}: {e}")

final_count = len(os.listdir(IMAGES_DIR))
print(f"\nDownload complete! Total images: {final_count}/194")