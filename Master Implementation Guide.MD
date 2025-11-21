Fashion Boutique WhatsApp AI Sales Agent - Complete System

🚀 MISSION STATEMENT
You are building a revolutionary multi-tenant SaaS platform that enables fashion boutiques in Kenya and East Africa to automate their sales through AI-powered WhatsApp agents. Each boutique gets their own intelligent sales assistant that can understand product images, make personalized recommendations, and process M-Pesa payments - all through natural WhatsApp conversations.

📊 PRODUCT OVERVIEW
What Makes This Special?

Image-First Shopping: Customers send photos of clothes they like, AI finds similar items
Personalized Experience: Size recommendations based on purchase history
Seamless Payments: M-Pesa STK push integration (no leaving WhatsApp)
Multi-Tenant: One platform serves hundreds of boutiques
No App Required: Everything happens in WhatsApp (2B+ users globally)

Target Market

Primary: Fashion boutiques in Nairobi, Mombasa, Kisumu (Kenya)
Secondary: Uganda, Tanzania, Rwanda (M-Pesa available)
Size: Small to medium boutiques (5-100 products)
Pain Point: Can't afford dedicated e-commerce sites or staff for 24/7 customer service

Business Model

Freemium: First 100 conversations free
Customer (WhatsApp)
    │
    │ 1. Sends image: "Do you have this?"
    │
    ▼
WhatsApp Business API (Twilio/360Dialog)
    │
    │ 2. Webhook POST /webhook/whatsapp
    │
    ▼
FastAPI Backend
    │
    ├─> Download image from WhatsApp
    ├─> Get/Create customer in Supabase
    ├─> Load conversation state
    │
    ▼
LangGraph Agent State Machine
    │
    ├─> Node 1: Image Analysis (Gemini Vision)
    │   └─> Extract: type, color, style, pattern
    │
    ├─> Node 2: Product Search (Supabase pgvector)
    │   └─> Semantic + text search
    │
    ├─> Node 3: Size Recommendation
    │   └─> Query customer's order history
    │
    ├─> Node 4: Generate Response (Gemini)
    │   └─> Natural conversational response
    │
    ▼
Send to Customer
    │
    ├─> Text message with product info
    ├─> Product images (WhatsApp media)
    │
    ▼
Customer: "I'll take the blue one, size M"
    │
    ▼
LangGraph Continues...
    │
    ├─> Node 5: Cart Management
    │   └─> Add to cart, calculate total
    │
    ├─> Node 6: Checkout
    │   └─> Collect delivery address
    │
    ├─> Node 7: Payment (PayLink M-Pesa)
    │   └─> Initiate STK push
    │
    ▼
Customer's Phone
    │
    │ M-Pesa prompt appears
    │ Customer enters PIN
    │
    ▼
PayLink Webhook → /webhook/paylink/payment
    │
    ▼
FastAPI Backend
    │
    ├─> Update order status → "paid"
    ├─> Decrease inventory
    ├─> Send confirmation to customer
    ├─> Notify boutique owner
    │
    ▼
Order Complete ✅

┌──────────────────────────────────────────────────────────┐
│                 BOUTIQUE OWNER JOURNEY                    │
└──────────────────────────────────────────────────────────┘

Owner visits dashboard.yourdomain.com
    │
    ▼
Next.js Dashboard (Supabase Auth)
    │
    ├─> View today's sales, orders, conversations
    ├─> Manage products (add, edit, delete)
    ├─> Upload images to Supabase Storage
    ├─> View customer database
    ├─> Analytics charts (Recharts)
    │
    ▼
Real-time Updates
    │
    └─> Supabase real-time subscription
        └─> "New order!" notification when order created

🎯 DEVELOPMENT ROADMAP
Phase 1: MVP Foundation (Days 1-7)
Day 1-2: Database & Infrastructure

 Set up Supabase project
 Create complete database schema
 Enable pgvector extension
 Create storage buckets
 Set up Row Level Security policies
 Seed test data (1 boutique, 10 products)

Day 3-4: Core Agent Logic

 Implement LangGraph state machine
 Build image analysis node (Gemini Vision)
 Build product search node (semantic + text)
 Build size recommendation logic
 Build conversational response generation
 Test complete flow end-to-end

Day 5-6: WhatsApp Integration

 Set up Twilio WhatsApp sandbox
 Implement webhook handler
 Test receiving messages & images
 Test sending messages & images
 Implement conversation state persistence

Day 7: Payment Integration

 Set up PayLink sandbox
 Implement M-Pesa STK push
 Handle payment webhooks
 Test complete purchase flow
 Handle payment failures gracefully

Phase 2: Dashboard (Days 8-14)
Day 8-9: Dashboard Foundation

 Next.js setup with TypeScript
 Supabase Auth integration
 Layout: Sidebar, Navbar, Footer
 Dashboard homepage (overview metrics)

Day 10-11: Product Management

 Products list page with table
 Add product form
 Edit product form
 Image upload to Supabase Storage
 Bulk CSV import

Day 12-13: Order Management

 Orders list with filters
 Order detail view
 Update order status
 Real-time order notifications

Day 14: Analytics & Polish

 Sales charts (daily, weekly, monthly)
 Top products view
 Customer segments
 Conversation history view
 Settings page

Phase 3: Multi-Tenant & Scaling (Days 15-21)
Day 15-16: Multi-Tenant Setup

 Boutique onboarding flow
 Boutique settings page
 WhatsApp number provisioning
 M-Pesa configuration per boutique

Day 17-18: Advanced Features

 Advanced product recommendations
 Automated marketing (abandoned cart)
 Inventory low stock alerts
 Customer segmentation

Day 19-20: Performance & Security

 Database query optimization
 Image compression pipeline
 Rate limiting on webhooks
 Security audit
 Load testing

Day 21: Deployment

 Deploy backend to Railway
 Deploy frontend to Vercel
 Configure production WhatsApp number
 Set up monitoring (Langfuse, Sentry)
 Documentation


💻 CRITICAL IMPLEMENTATION DETAILS
1. LangGraph State Machine Design
The agent operates as a state machine with conditional routing:
python# Routing logic
def route_next_step(state: AgentState) -> str:
    step = state["current_step"]
    
    # Image uploaded → analyze it
    if step == "start" and state.get("uploaded_image_url"):
        return "analyze_image"
    
    # Analysis complete → search products
    elif step == "image_analyzed":
        return "search_products"
    
    # Products found → recommend size
    elif step == "products_found":
        return "recommend_size"
    
    # Size recommended → generate response
    elif step == "size_recommended":
        return "generate_response"
    
    # Waiting for product selection
    elif step == "awaiting_product_selection":
        last_msg = state["messages"][-1]["content"].lower()
        if any(word in last_msg for word in ["first", "1", "blue", "red"]):
            return "handle_selection"
        else:
            return "generate_response"  # Clarification needed
    
    # Cart updated → checkout or continue?
    elif step == "cart_updated":
        last_msg = state["messages"][-1]["content"].lower()
        if "checkout" in last_msg or "pay" in last_msg:
            return "checkout"
        else:
            return "generate_response"  # Continue shopping
    
    # Got delivery address → initiate payment
    elif step == "awaiting_delivery_address":
        return "payment"
    
    # Payment initiated → wait for webhook
    elif step == "payment_initiated":
        return END
    
    # Order completed
    elif step == "order_completed":
        return END
    
    else:
        return END

# Build graph
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("analyze_image", analyze_product_image)
workflow.add_node("search_products", search_matching_products)
workflow.add_node("recommend_size", recommend_size)
workflow.add_node("generate_response", generate_product_response)
workflow.add_node("handle_selection", handle_product_selection)
workflow.add_node("checkout", initiate_checkout)
workflow.add_node("payment", initiate_payment)

# Conditional edges
workflow.add_conditional_edges("analyze_image", route_next_step)
workflow.add_conditional_edges("search_products", route_next_step)
# ... etc for all nodes

workflow.set_entry_point("analyze_image")
agent = workflow.compile()
2. Conversation State Persistence
Critical: State MUST persist between messages (customer can reply hours later):
pythonasync def process_whatsapp_message(from_number: str, message_body: str, image_url: str = None):
    # Load existing conversation
    conversation = await supabase.table("conversations").select("*").eq(
        "customer_phone", from_number
    ).single().execute()
    
    if conversation.data:
        # Resume existing conversation
        state = conversation.data["state"]
    else:
        # Start new conversation
        state = create_initial_state(from_number)
    
    # Add new message
    state["messages"].append({
        "role": "user",
        "content": message_body,
        "image_url": image_url,
        "timestamp": datetime.now().isoformat()
    })
    
    # Run agent
    result = await agent.ainvoke(state)
    
    # Save updated state
    await supabase.table("conversations").upsert({
        "customer_phone": from_number,
        "state": result,
        "current_step": result["current_step"],
        "last_message_at": "now()"
    }).execute()
    
    # Send response
    response_text = result["messages"][-1]["content"]
    await send_whatsapp_message(from_number, response_text)
3. Size Recommendation Algorithm
pythonasync def recommend_size(state: AgentState) -> AgentState:
    customer_id = state["customer_id"]
    
    # Get customer's past orders
    orders = await supabase.table("orders").select(
        "items"
    ).eq("customer_id", customer_id).eq(
        "payment_status", "paid"
    ).order("created_at", desc=True).limit(10).execute()
    
    # Extract size patterns
    size_frequency = {}
    for order in orders.data:
        for item in order["items"]:
            size = item.get("size")
            if size:
                size_frequency[size] = size_frequency.get(size, 0) + 1
    
    if size_frequency:
        # Most common size
        preferred_size = max(size_frequency, key=size_frequency.get)
        confidence = "high" if len(orders.data) >= 3 else "medium"
        
        state["customer_size_profile"] = {
            "preferred_size": preferred_size,
            "size_history": size_frequency,
            "confidence": confidence
        }
        state["recommended_size"] = preferred_size
    else:
        # No history
        state["customer_size_profile"] = {
            "preferred_size": None,
            "confidence": "low"
        }
    
    return state
4. Product Search Strategy
Three-tier search approach:

Vector Search (best for "vibes" and visual similarity)
Full-Text Search (good for specific terms)
Filtered Search (fallback with category/color filters)

pythonasync def search_products_comprehensive(query: str, boutique_id: str, analysis: dict):
    results = []
    
    # Tier 1: Vector semantic search
    vector_results = await search_vector(query, boutique_id)
    results.extend(vector_results)
    
    # Tier 2: Full-text search
    if len(results) < 3:
        text_results = await search_fulltext(query, boutique_id)
        results.extend([r for r in text_results if r not in results])
    
    # Tier 3: Filtered search
    if len(results) < 3:
        filtered_results = await search_filtered(
            boutique_id=boutique_id,
            category=analysis["product_type"],
            colors=analysis["colors"],
            style=analysis["style_category"]
        )
        results.extend([r for r in filtered_results if r not in results])
    
    return results[:5]  # Top 5
5. Payment Flow with Error Handling
pythonasync def initiate_payment(state: AgentState) -> AgentState:
    try:
        # Create order first
        order = await create_order(state)
        
        # Initiate M-Pesa STK push
        response = await mpesa_client.call_tool("stk_push", {
            "amount": str(int(state["total_amount"])),
            "phone_number": state["customer_phone"],
            "account_reference": order["order_number"],
            "transaction_desc": f"Order {order['order_number']}"
        })
        
        state["payment_initiated"] = True
        state["checkout_request_id"] = response["CheckoutRequestID"]
        state["order_id"] = order["id"]
        
        state["messages"].append({
            "role": "assistant",
            "content": f"💳 Payment request sent!\n\n"
                      f"Check your phone for M-Pesa prompt.\n"
                      f"Amount: KES {state['total_amount']}\n"
                      f"Order: {order['order_number']}\n\n"
                      f"Enter your PIN to complete payment."
        })
        
    except Exception as e:
        print(f"Payment error: {e}")
        
        # Graceful degradation
        state["messages"].append({
            "role": "assistant",
            "content": "Sorry, payment failed. Please try again or "
                      "contact us for manual payment options."
        })
        state["current_step"] = "payment_failed"
    
    return state

# Webhook handler
@app.post("/webhook/paylink/payment")
async def handle_payment_callback(request: Request):
    payload = await request.json()
    
    if payload["ResultCode"] == 0:
        # Success
        order_id = payload["account_reference"]
        await supabase.table("orders").update({
            "payment_status": "paid",
            "mpesa_receipt": payload["MpesaReceiptNumber"],
            "paid_at": "now()"
        }).eq("order_number", order_id).execute()
        
        # Send confirmation to customer
        # Update inventory
        # Notify owner
    else:
        # Failed
        # Send failure message
        # Log reason
    
    return {"status": "ok"}

🎨 DASHBOARD UI/UX GUIDELINES
Design Principles

Clean & Minimal: No clutter, focus on key metrics
Mobile-First: Most owners will use phones
Real-Time: Live updates for orders, conversations
Data-Driven: Charts and metrics everywhere
Fast: < 2s page loads

Key Pages & Features
1. Dashboard Overview

Today's sales (number & revenue)
Pending orders count
Active conversations
Low stock alerts
Top selling products (last 7 days)
Sales trend chart (line graph)

2. Products Page

Data table with search & filters
Quick actions: Edit, Duplicate, Delete
Bulk upload CSV
Stock status indicators
Image thumbnails

3. Orders Page

Filterable table (status, date, amount)
Order detail modal
Status update dropdown
Print receipt button
Customer info link

4. Conversations Page

List of recent conversations
Click to view full history
Customer details sidebar
Quick reply feature

5. Analytics Page

Revenue over time (chart)
Products sold breakdown (pie chart)
Customer acquisition (line chart)
Conversion funnel
Average order value

Component Library (shadcn/ui)
Use these pre-built components:

Button, Input, Select, Textarea
Table, Card, Badge, Avatar
Dialog, Sheet, Tabs
Form, Label, Checkbox
Toast notifications
Command palette (Cmd+K search)


🔒 SECURITY BEST PRACTICES
1. Webhook Signature Verification
pythonimport hmac
import hashlib

def verify_twilio_signature(request_url: str, params: dict, signature: str):
    """Verify Twilio webhook signature"""
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    # Create signature
    data = request_url + ''.join([f'{k}{params[k]}' for k in sorted(params.keys())])
    expected = base64.b64encode(
        hmac.new(
            auth_token.encode(),
            data.encode(),
            hashlib.sha1
        ).digest()
    ).decode()
    
    return hmac.compare_digest(signature, expected)
2. Rate Limiting
pythonfrom fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/webhook/whatsapp")
@limiter.limit("100/minute")  # Max 100 messages per minute per boutique
async def handle_webhook():
    ...
3. Input Sanitization
pythondef sanitize_user_input(text: str) -> str:
    # Remove SQL injection attempts
    # Remove XSS attempts
    # Trim whitespace
    return text.strip()[:500]  # Max 500 chars
4. Environment Variables (Never Hardcode!)
pythonfrom pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    anthropic_api_key: str
    twilio_auth_token: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

📈 MONITORING & OBSERVABILITY
Langfuse Integration
pythonfrom langfuse import Langfuse

langfuse = Langfuse()

# Trace entire conversation
trace = langfuse.trace(
    name="whatsapp_conversation",
    user_id=customer_id,
    metadata={"boutique_id": boutique_id}
)

# Track image analysis
trace.span(
    name="image_analysis",
    input={"image_url": url},
    output=analysis
)

# Track product search
trace.span(
    name="product_search",
    input={"query": query},
    output={"results_count": len(products)}
)

# Track costs
trace.update(
    output=final_response,
    usage={
        "input_tokens": 1200,
        "output_tokens": 350,
        "total_cost": 0.012  # USD
    }
)
Error Tracking
pythonimport sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)

try:
    result = await agent.ainvoke(state)
except Exception as e:
    sentry_sdk.capture_exception(e)
    # Graceful fallback

🚀 DEPLOYMENT CHECKLIST
Pre-Deployment

 All environment variables set in production
 Database migrations applied
 RLS policies tested
 Webhook URLs configured
 Payment webhooks tested with sandbox
 Security audit passed
 Load testing completed (100 concurrent users)
 Error handling tested
 Monitoring set up

Deployment Steps

Deploy Backend to Railway

bash   railway login
   railway init
   railway up

Deploy Frontend to Vercel

bash   vercel login
   vercel --prod

Configure DNS

Point api.yourdomain.com → Railway
Point dashboard.yourdomain.com → Vercel


Update Webhooks

Twilio: https://api.yourdomain.com/webhook/whatsapp
PayLink: https://api.yourdomain.com/webhook/paylink/payment


Test Production Flow End-to-End

Post-Deployment

 Monitor error rates (first 24 hours)
 Check performance metrics
 Verify payments working
 Test with real customers
 Set up alerts for downtime
 Document any issues


🎯 SUCCESS CRITERIA
Technical Metrics

✅ 99.9% uptime
✅ < 2s response time for messages
✅ < 5s for image analysis
✅ 95%+ payment success rate
✅ Zero data leaks between boutiques

Business Metrics

✅ 10 paying boutiques in first month
✅ 70%+ conversation-to-purchase rate
✅ $30k+ processed through platform monthly
✅ 4.5+ star customer satisfaction


💡 KEY PRINCIPLES TO REMEMBER

Always Async: Use async/await for all I/O operations
✅ Complete database schema (Supabase)
✅ Full backend architecture (FastAPI + LangGraph)
✅ Dashboard design (Next.js + React)
✅ Payment integration (PayLink M-Pesa)
✅ WhatsApp integration (Twilio)
✅ Multi-tenant patterns
✅ Security best practices
✅ Deployment strategy

When you encounter decisions:

Prioritize simplicity over clever solutions
Optimize for developer experience
Make it work, then make it fast
Documentation as code

When you encounter errors:

Check Langfuse traces first
Verify webhook signatures
Check Supabase RLS policies
Test with curl/Postman

When you're ready:
Start with Phase 1, Day 1 and build iteratively. Each component should work independently before integration.
Good luck building! 🚀