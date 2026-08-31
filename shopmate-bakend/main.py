import os
import json
import re
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name("api.env"))

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY", "")
has_gemini_key = bool(api_key and api_key != "your_key_here")
if has_gemini_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def service_status():
    return {
        "service": "ShopMate backend",
        "status": "ok",
        "mode": "gemini" if has_gemini_key else "demo"
    }

# --- MOCK DATA (Demo Mode) ---
DEMO_PRODUCTS = [
    {"id": 1, "name": "Apple MacBook Air M3", "price": 114900, "brand": "Apple", "rating": 4.8, "match": 95, "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&auto=format&fit=crop"},
    {"id": 2, "name": "Samsung Galaxy S24 Ultra", "price": 129999, "brand": "Samsung", "rating": 4.7, "match": 92, "img": "https://images.unsplash.com/photo-1598327105666-5b89351?w=400&auto=format&fit=crop"},
    {"id": 3, "name": "Sony WH-1000XM5", "price": 29990, "brand": "Sony", "rating": 4.9, "match": 88, "img": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&auto=format&fit=crop"},
    {"id": 4, "name": "OnePlus Nord 4", "price": 29999, "brand": "OnePlus", "rating": 4.5, "match": 90, "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&auto=format&fit=crop"},
    {"id": 5, "name": "Lenovo IdeaPad Slim 3", "price": 44990, "brand": "Lenovo", "rating": 4.3, "match": 86, "img": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&auto=format&fit=crop"},
    {"id": 6, "name": "Samsung Galaxy A55", "price": 39999, "brand": "Samsung", "rating": 4.4, "match": 89, "img": "https://images.unsplash.com/photo-1512499617640-c2f999098c01?w=400&auto=format&fit=crop"},
    {"id": 7, "name": "Redmi Note 14 Pro", "price": 24999, "brand": "Redmi", "rating": 4.2, "match": 85, "img": "https://images.unsplash.com/photo-1523206489230-c012c64b2b48?w=400&auto=format&fit=crop"},
    {"id": 8, "name": "HP 15s Laptop", "price": 47990, "brand": "HP", "rating": 4.2, "match": 84, "img": "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&auto=format&fit=crop"},
    {"id": 9, "name": "ASUS Vivobook 15", "price": 49990, "brand": "ASUS", "rating": 4.3, "match": 87, "img": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&auto=format&fit=crop"},
    {"id": 10, "name": "Sony WF-1000XM5 Earbuds", "price": 24990, "brand": "Sony", "rating": 4.6, "match": 91, "img": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&auto=format&fit=crop"},
    {"id": 11, "name": "Nothing Phone (2a)", "price": 23999, "brand": "Nothing", "rating": 4.3, "match": 88, "img": "https://images.unsplash.com/photo-1598327105666-5b89351?w=400&auto=format&fit=crop"},
    {"id": 12, "name": "Vivo V30", "price": 33999, "brand": "Vivo", "rating": 4.4, "match": 87, "img": "https://images.unsplash.com/photo-1512499617640-c2f999098c01?w=400&auto=format&fit=crop"},
    {"id": 13, "name": "Realme GT 6T", "price": 30999, "brand": "Realme", "rating": 4.3, "match": 86, "img": "https://images.unsplash.com/photo-1523206489230-c012c64b2b48?w=400&auto=format&fit=crop"},
    {"id": 14, "name": "Motorola Edge 50 Fusion", "price": 22999, "brand": "Motorola", "rating": 4.2, "match": 84, "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&auto=format&fit=crop"},
    {"id": 15, "name": "Acer Aspire 5", "price": 42990, "brand": "Acer", "rating": 4.2, "match": 83, "img": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&auto=format&fit=crop"},
    {"id": 16, "name": "Dell Inspiron 15", "price": 48990, "brand": "Dell", "rating": 4.3, "match": 85, "img": "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&auto=format&fit=crop"},
    {"id": 17, "name": "MSI Modern 14", "price": 49990, "brand": "MSI", "rating": 4.4, "match": 86, "img": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&auto=format&fit=crop"},
    {"id": 18, "name": "Microsoft Surface Laptop Go", "price": 47990, "brand": "Microsoft", "rating": 4.4, "match": 88, "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&auto=format&fit=crop"}
]

PRODUCT_SPECS = {
    1: (8, 256), 2: (12, 256), 3: (0, 0), 4: (8, 128), 5: (8, 512),
    6: (8, 128), 7: (8, 256), 8: (8, 512), 9: (16, 512), 10: (0, 0),
    11: (8, 128), 12: (8, 256), 13: (8, 128), 14: (8, 128), 15: (16, 512),
    16: (8, 512), 17: (16, 512), 18: (8, 256)
}
for product in DEMO_PRODUCTS:
    ram, storage = PRODUCT_SPECS[product["id"]]
    product["ram"] = f"{ram} GB" if ram else "Not applicable"
    product["storage"] = f"{storage} GB" if storage else "Not applicable"

def search_demo_products(message: str):
    query = message.lower()
    brands = ("apple", "samsung", "sony", "oneplus", "lenovo", "redmi", "hp", "asus", "nothing", "vivo", "realme", "motorola", "acer", "dell", "msi", "microsoft")
    requested_brand = next((brand for brand in brands if brand in query), None)
    category_terms = {
        "laptop": ("laptop", "macbook", "computer", "coding", "notebook", "aspire", "inspiron", "modern", "surface"),
        "phone": ("phone", "mobile", "smartphone", "galaxy", "iphone", "vivo", "realme", "motorola", "nothing"),
        "headphones": ("headphone", "headphones", "earphone", "earbuds", "audio")
    }
    requested_categories = [
        category for category, terms in category_terms.items()
        if any(term in query for term in terms)
    ]

    category_matches = {
        "laptop": ("laptop", "macbook", "ideapad", "aspire", "inspiron", "modern", "surface"),
        "phone": ("phone", "galaxy", "oneplus", "vivo", "realme", "motorola", "nothing"),
        "headphones": ("headphone", "audio")
    }
    products = [
        product for product in DEMO_PRODUCTS
        if (not requested_categories or any(
            any(term in product["name"].lower() for term in category_matches[category])
            for category in requested_categories
        ))
        and (not requested_brand or product["brand"].lower() == requested_brand)
    ]

    def amount(value: str, unit: str = ""):
        value = float(value.replace(",", ""))
        if unit in ("k", "thousand"):
            value *= 1000
        elif unit in ("lakh", "l"):
            value *= 100000
        return value

    range_match = re.search(
        r"(?:between|from)\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\s*(?:and|to)\s*"
        r"(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(k|thousand|l)?",
        query
    )
    upper_match = re.search(
        r"(?:under|below|less than|within|upto|up to)\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(k|thousand|lakh|l)?",
        query
    )
    minimum = maximum = None
    if range_match:
        minimum = amount(range_match.group(1), range_match.group(2) or "")
        maximum = amount(range_match.group(3), range_match.group(4) or "")
    elif upper_match:
        maximum = amount(upper_match.group(1), upper_match.group(2) or "")

    if minimum is not None:
        products = [product for product in products if minimum <= product["price"] <= maximum]
    elif maximum is not None:
        products = [product for product in products if product["price"] <= maximum]

    category_label = ", ".join(requested_categories) if requested_categories else requested_brand or "all"
    budget = {"min": minimum, "max": maximum} if minimum is not None else maximum
    return products, category_label, budget

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
async def chat_with_mira(request: ChatRequest):
    if not has_gemini_key:
        products, category, budget = search_demo_products(request.message)
        if products:
            product_summary = ", ".join(f'{product["name"]} (₹{product["price"]:,})' for product in products)
            reply = f"I found {len(products)} {category} match(es): {product_summary}."
        else:
            reply = "I could not find a matching product in the demo catalog. Try a different category or budget."
        return {
            "reply": reply,
            "recommended_products": products,
            "intent": "search",
            "extracted_requirements": {"budget": budget or "", "category": category}
        }

    system_prompt = f"""
    You are MIRA (Multimodal Intelligent Retail Assistant). 
    Help the user shop. Support English, Hindi, and Hinglish.
    Current available demo products: {json.dumps(DEMO_PRODUCTS)}
    
    Response format (JSON):
    {{
        "reply": "Natural language response in user's language",
        "recommended_products": [], 
        "intent": "search|compare|general",
        "extracted_requirements": {{"budget": "", "category": ""}}
    }}
    """
    
    full_prompt = f"{system_prompt}\nUser: {request.message}"
    response = model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

@app.post("/api/vision")
async def vision_search(image: UploadFile = File(...)):
    # Simple Vision Logic
    img_data = await image.read()
    img_part = {"mime_type": "image/jpeg", "data": img_data}
    prompt = "Identify this product and give its category and estimated price in INR."
    response = model.generate_content([prompt, img_part])
    return {"analysis": response.text, "products": DEMO_PRODUCTS[:2]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)