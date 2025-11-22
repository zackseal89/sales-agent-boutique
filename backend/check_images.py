import asyncio
from services.supabase_service import supabase_service

async def check_images():
    try:
        # Search for "dress" or just get all products
        products = await supabase_service.search_products_by_text(
            boutique_id="boutique_123", # Assuming default ID
            query="dress",
            limit=5
        )
        
        print(f"Found {len(products)} products")
        for p in products:
            print(f"Name: {p['name']}")
            print(f"Image URLs: {p.get('image_urls')}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_images())
