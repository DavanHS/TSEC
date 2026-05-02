#!/usr/bin/env python3
"""
Generate Gemini embeddings for products and save to products.json
Uses gemini-embedding-001 (768-dim stable model)
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PRODUCTS_FILE = os.path.join(PROJECT_DIR, "data/products.json")
GEMINI_MODEL = "gemini-embedding-001"  # Stable 768-dim model

def load_products():
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=2)

def get_embedding(client, text):
    result = client.embed_content(
        model=GEMINI_MODEL,
        content=text
    )
    return result['embedding']

def main():
    env_file = os.path.join(PROJECT_DIR, ".env")
    api_key = None
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("ERROR: No valid GEMINI_API_KEY found in .env")
        sys.exit(1)
    
    print(f"Using model: {GEMINI_MODEL} (768-dim, stable)")
    
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print(f"Loading products from {PRODUCTS_FILE}...")
    products = load_products()
    print(f"Found {len(products)} products")
    
    # Clear existing embeddings
    for p in products:
        if 'embedding' in p:
            del p['embedding']
    save_products(products)
    print("Cleared existing embeddings")
    
    # Generate new embeddings
    for i, product in enumerate(products):
        text = f"{product['name']} {product['description']} {' '.join(product.get('features', []))}"
        print(f"[{i+1}/{len(products)}] Embedding: {product['id']} - {product['name'][:30]}...")
        
        try:
            embedding = get_embedding(genai, text)
            product['embedding'] = embedding
        except Exception as e:
            print(f"ERROR: {e}")
            continue
    
    print(f"\nSaving to {PRODUCTS_FILE}...")
    save_products(products)
    
    with_embedding = sum(1 for p in products if p.get('embedding'))
    print(f"\n✅ Done! {with_embedding}/{len(products)} products now have {GEMINI_MODEL} embeddings")

if __name__ == "__main__":
    main()