import asyncio
from services.supabase_service import supabase_service

async def update_product_images():
    print("🔄 Updating product images to public URLs...")
    
    # Public image URLs from Unsplash
    image_map = {
        "gown": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=800&auto=format&fit=crop",
        "dress": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=800&auto=format&fit=crop",
        "shirt": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=800&auto=format&fit=crop",
        "shoes": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=800&auto=format&fit=crop"
    }
    
    try:
        # Get all products directly from table (bypass search function)
        response = supabase_service.client.table("products").select("*").execute()
        products = response.data
        
        print(f"Found {len(products)} products to update.")
        
        for p in products:
            name_lower = p['name'].lower()
            new_url = None
            
            if "gown" in name_lower or "dress" in name_lower:
                new_url = image_map["gown"]
            elif "shirt" in name_lower or "top" in name_lower:
                new_url = image_map["shirt"]
            elif "shoe" in name_lower or "heel" in name_lower:
                new_url = image_map["shoes"]
            else:
                new_url = image_map["dress"]
                
            if new_url:
                print(f"Updating {p['name']}...")
                supabase_service.client.table("products").update({
                    "image_urls": [new_url]
                }).eq("id", p['id']).execute()
                print(f"✅ Updated {p['name']}")
                
        print("\n🎉 All images updated to public URLs!")
            
    except Exception as e:
        print(f"❌ Error updating images: {e}")

if __name__ == "__main__":
    asyncio.run(update_product_images())
