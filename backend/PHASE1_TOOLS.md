# Phase 1 Tools - Quick Reference

## Available Tools

### 1. Product Search
**Tool:** `search_products`
**Usage:** "Show me dresses under 3000 KES"
**Features:**
- Text search
- Category filter
- Price range (min/max)
- Returns top 5 matches

### 2. Add to Cart
**Tool:** `add_to_cart`
**Usage:** "Add the blue dress to my cart in size M"
**Features:**
- Adds product with size
- Updates quantity if already in cart
- Returns cart summary

### 3. View Cart
**Tool:** `get_cart_summary`
**Usage:** "What's in my cart?"
**Features:**
- Shows all cart items
- Displays subtotal
- Item count

### 4. Check Inventory
**Tool:** `check_inventory`
**Usage:** "Do you have this in size L?"
**Features:**
- Real-time stock check
- Size-specific availability
- Quantity available

### 5. Order Status
**Tool:** `get_order_status`
**Usage:** "Where is my order ORD-123?"
**Features:**
- Order details
- Current status
- Payment status

### 6. Order History
**Tool:** `get_customer_orders`
**Usage:** "Show me my previous orders"
**Features:**
- List of customer orders
- Optional status filter
- Most recent first

## Testing

### Run All Tests
```bash
cd backend
python test_tools_phase1.py
```

### Run Existing Agent Tests
```bash
cd backend
python test_agent.py
```

## Example Conversations

### Shopping Flow
1. **User:** "Show me dresses under 3000 KES"
   - **Tool:** search_products(query="dresses", max_price=3000)
   
2. **User:** "Add the first one to my cart in size M"
   - **Tool:** add_to_cart(product_id="...", size="M")
   
3. **User:** "What's in my cart?"
   - **Tool:** get_cart_summary()

### Order Tracking
1. **User:** "Where is my order?"
   - **Tool:** get_customer_orders()
   
2. **User:** "Check order ORD-123"
   - **Tool:** get_order_status(order_id="ORD-123")

## Database Tables Required

Make sure these tables exist in Supabase:
- `products` - Product catalog
- `cart_items` - Shopping cart items
- `inventory` - Stock levels by size
- `orders` - Customer orders
- `customers` - Customer information

## Environment Variables

Required in `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
GOOGLE_API_KEY=your_gemini_api_key
PAYLINK_API_KEY=your_paylink_key (optional for dev)
```

## Next Steps

Phase 2 tools to implement:
- Size recommendations
- Image analysis enhancements
- Price & promotions
- Customer preferences
