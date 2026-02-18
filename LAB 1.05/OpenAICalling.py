import os
from openai import OpenAI
from dotenv import load_dotenv
from datasets import load_dataset
import base64
from io import BytesIO
import json
from pathlib import Path
import time

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Create results folder
Path("results").mkdir(exist_ok=True)

print("\n Starting Product Listing Generator...\n")

# Load 3 products
print("Loading products...")
dataset = load_dataset("ashraq/fashion-product-images-small", split="train[:3]")
print(f"✓ Loaded {len(dataset)} products\n")

results = []

for i, product in enumerate(dataset):
    print(f"[{i+1}/3] Processing: {product['productDisplayName']}")
    
    # Convert image to base64
    buffered = BytesIO()
    product['image'].convert('RGB').save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create prompt
    prompt = f"""Create a product listing for this {product['masterCategory']} item.

Product name: {product['productDisplayName']}

Return ONLY a JSON object with:
- title (catchy, under 60 characters)
- description (150-200 words)
- features (5-7 bullet points as an array)
- keywords (10-15 keywords as a string)
- Highlight key features and benefits

Example format:
{{"title": "...", "description": "...", "features": ["...", "..."], "keywords": "..."}}"""
    
    # Call API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]
            }],
            max_tokens=800
        )
        
        # Get response
        text = response.choices[0].message.content
        
        # Clean JSON if needed
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        listing = json.loads(text)
        
        results.append({
            "product_id": i + 1,
            "name": product['productDisplayName'],
            "listing": listing
        })
        
        print(f"   ✓ Done!\n")
        time.sleep(1)
        
    except Exception as error:
        print(f"   ❌ Error: {error}\n")

# Save results
print(f"Saving results...")

# Save JSON
with open("results/listings.json", "w") as f:
    json.dump(results, f, indent=2)

# Save readable version
with open("results/listings.txt", "w") as f:
    f.write("GENERATED PRODUCT LISTINGS\n")
    f.write("=" * 80 + "\n\n")
    
    for r in results:
        f.write(f"Product {r['product_id']}: {r['name']}\n")
        f.write(f"Title: {r['listing']['title']}\n")
        f.write(f"Description: {r['listing']['description']}\n")
        f.write(f"Features: {', '.join(r['listing']['features'])}\n")
        f.write(f"Keywords: {r['listing']['keywords']}\n")
        f.write("\n" + "=" * 80 + "\n\n")

print(f"✅ DONE! Generated {len(results)} listings")
print(f"Check these files:")
print(f"   - results/listings.json")
print(f"   - results/listings.txt\n")








