You are now setting up the complete technical stack for the Fashion Boutique WhatsApp AI Agent platform. We use Supabase as our backend infrastructure.

## TECHNOLOGY STACK DETAILS

### Backend Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.109+
- **AI Framework**: LangGraph + LangChain
- **AI Model**: Google Gemini 2.0 Flash (gemini-2.0-flash-exp) or Gemini 1.5 Pro
- **Database**: Supabase (PostgreSQL 15+ with pgvector)
- **Payment**: PayLink SDK for M-Pesa
- **WhatsApp**: Twilio WhatsApp Business API or 360Dialog
- **Observability**: Langfuse
- **Image Processing**: Pillow (PIL)
- **Async**: asyncio + httpx

### Frontend Stack (Dashboard)
- **Framework**: Next.js 14+ (React 18)
- **Language**: TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React Query + Zustand
- **Supabase Client**: @supabase/supabase-js
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod validation
- **Tables**: TanStack Table

### Infrastructure (Serverless)
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage (for product images)
- **Auth**: Supabase Auth
- **Backend**: Google Cloud Run (serverless FastAPI containers)
- **Frontend**: Vercel (Next.js)
- **Background Jobs**: Google Cloud Tasks
- **Secrets**: Google Secret Manager
- **Region**: africa-south1 (Johannesburg, South Africa)
- **CDN**: Google Cloud CDN + Supabase CDN
- **Monitoring**: Google Cloud Monitoring + Langfuse

## SUPABASE SETUP GUIDE

### Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Create new project
3. Choose region closest to Kenya (e.g., AWS ap-south-1 Mumbai or eu-west-1 Ireland)
4. Save your project URL and API keys:
   - `SUPABASE_URL`: https://xxxxx.supabase.co
   - `SUPABASE_ANON_KEY`: eyJxxx... (public, safe for frontend)
   - `SUPABASE_SERVICE_KEY`: eyJxxx... (secret, backend only)

### Step 2: Enable pgvector Extension
In Supabase SQL Editor, run:
````sql
-- Enable vector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;
````

### Step 3: Complete Database Schema

Run this complete schema in Supabase SQL Editor:
````sql
-- =====================================================
-- SEED DATA FOR TESTING
-- =====================================================

-- Insert test boutique
INSERT INTO boutiques (
    id, name, whatsapp_number, owner_name, owner_email, 
    owner_whatsapp, subscription_status, is_active, onboarding_completed
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Nairobi Fashion House',
    '254712345678',
    'Jane Wanjiku',
    'jane@nairobi-fashion.com',
    '254712345678',
    'active',
    true,
    true
);

-- Insert sample products
INSERT INTO products (boutique_id, name, description, category, price, sizes, colors, stock_quantity, tags, image_urls) VALUES
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Floral Summer Dress',
    'Beautiful flowing dress with vibrant floral patterns. Perfect for casual outings and summer parties. Made from breathable cotton blend.',
    'dresses',
    2500.00,
    '["S", "M", "L", "XL"]'::jsonb,
    '["blue", "pink", "yellow"]'::jsonb,
    15,
    '["summer", "casual", "floral", "trending"]'::jsonb,
    '["https://example.com/dress1.jpg"]'::jsonb
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Elegant Evening Gown',
    'Stunning floor-length gown for special occasions. Features elegant draping and flattering silhouette.',
    'dresses',
    4500.00,
    '["S", "M", "L"]'::jsonb,
    '["red", "black", "navy"]'::jsonb,
    8,
    '["formal", "evening", "party", "wedding"]'::jsonb,
    '["https://example.com/gown1.jpg"]'::jsonb
);
````

### Step 4: Configure Supabase Storage

Create storage buckets for product images:
````sql
-- Create storage bucket for product images
INSERT INTO storage.buckets (id, name, public) 
VALUES ('product-images', 'product-images', true);

-- Allow public read access
CREATE POLICY "Public Access to Product Images"
ON storage.objects FOR SELECT
USING (bucket_id = 'product-images');

-- Allow authenticated users to upload (boutique owners)
CREATE POLICY "Authenticated users can upload product images"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'product-images' AND 
    auth.role() = 'authenticated'
);
````

### Step 5: Supabase MCP Configuration

To allow AI agent to interact with Supabase:

**Install Supabase MCP Server:**
````bash
npm install -g @supabase/mcp-server
````

**Configure MCP settings** (for Claude Desktop or API):
````json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "@supabase/mcp-server"
      ],
      "env": {
        "SUPABASE_URL": "https://xxxxx.supabase.co",
        "SUPABASE_SERVICE_KEY": "eyJxxx..."
      }
    }
  }
}
````

## ENVIRONMENT VARIABLES

Create `.env` file in backend:
````bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_KEY=eyJxxx...

# Google Gemini
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# WhatsApp (Choose one)
# Option A: Twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# Option B: 360Dialog
THREESIXTY_DIALOG_API_KEY=xxxxx
THREESIXTY_DIALOG_PARTNER_ID=xxxxx

# PayLink M-Pesa
PAYLINK_API_KEY=your_paylink_key
PAYLINK_PROJECT=your_project_name
MPESA_BUSINESS_SHORTCODE=174379
MPESA_CONSUMER_KEY=xxxxx
MPESA_CONSUMER_SECRET=xxxxx
MPESA_PASSKEY=xxxxx
MPESA_CALLBACK_URL=https://yourdomain.com/webhook/paylink/payment
MPESA_ENVIRONMENT=sandbox  # or 'production'

# Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk-xxx
LANGFUSE_SECRET_KEY=sk-xxx
LANGFUSE_HOST=https://cloud.langfuse.com

# Application
ENVIRONMENT=development
PORT=8080  # Cloud Run uses 8080 by default
WEBHOOK_BASE_URL=https://yourdomain.com  # Use ngrok for dev

# Google Cloud (for production)
GCP_PROJECT_ID=your-project-id
GCP_REGION=africa-south1
CLOUD_RUN_SERVICE_NAME=fashion-boutique-api
````

Create `.env.local` in dashboard (Next.js):
````bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
````

## BACKEND PYTHON REQUIREMENTS

Create `requirements.txt`:
````txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6

# LangChain & LangGraph
langchain==0.1.0
langchain-google-genai==1.0.0
langgraph==0.0.20
langsmith==0.0.77
google-generativeai==0.3.0

# Supabase
supabase==2.3.0
postgrest-py==0.13.0

# Async & HTTP
httpx==0.26.0
aiohttp==3.9.1

# WhatsApp
twilio==8.11.1

# Payments
paylink-sdk==1.0.0  # Hypothetical - use actual package

# Image Processing
Pillow==10.2.0

# Observability
langfuse==2.14.0

# Utils
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
asyncpg==0.29.0
````

## FRONTEND PACKAGE.JSON
````json
{
  "name": "fashion-boutique-dashboard",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.39.0",
    "@supabase/auth-helpers-nextjs": "^0.8.7",
    "@tanstack/react-query": "^5.17.9",
    "@tanstack/react-table": "^8.11.6",
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.49.3",
    "recharts": "^2.10.3",
    "zod": "^3.22.4",
    "zustand": "^4.4.7",
    "lucide-react": "^0.309.0",
    "date-fns": "^3.0.6",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "eslint": "^8",
    "eslint-config-next": "14.1.0",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
````

## SUPABASE CLIENT INITIALIZATION

**Backend (Python):**
````python
# backend/services/supabase_client.py
from supabase import create_client, Client
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Service client (bypasses RLS, for backend operations)
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

# Helper functions
async def get_boutique_by_phone(whatsapp_number: str):
    """Get boutique by WhatsApp number"""
    response = supabase.table("boutiques").select("*").eq(
        "whatsapp_number", whatsapp_number
    ).single().execute()
    return response.data

async def create_or_get_customer(boutique_id: str, whatsapp_number: str):
    """Create customer if doesn't exist"""
    response = supabase.table("customers").select("*").eq(
        "boutique_id", boutique_id
    ).eq("whatsapp_number", whatsapp_number).execute()
    
    if response.data:
        return response.data[0]
    
    # Create new customer
    new_customer = {
        "boutique_id": boutique_id,
        "whatsapp_number": whatsapp_number
    }
    response = supabase.table("customers").insert(new_customer).execute()
    return response.data[0]

async def save_conversation_state(conversation_id: str, state: dict):
    """Save LangGraph state to database"""
    supabase.table("conversations").upsert({
        "id": conversation_id,
        "state": state,
        "current_step": state.get("current_step"),
        "messages": state.get("messages", []),
        "cart": state.get("cart", []),
        "last_message_at": "now()"
    }).execute()

async def load_conversation_state(customer_id: str, boutique_id: str):
    """Load conversation state from database"""
    response = supabase.table("conversations").select("*").eq(
        "customer_id", customer_id
    ).eq("boutique_id", boutique_id).single().execute()
    
    if response.data:
        return response.data["state"]
    return None
````

**Frontend (Next.js):**
````typescript
// lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// lib/supabase/server.ts (for server components)
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
      },
    }
  )
}
````

## KEY INTEGRATION PATTERNS

### Pattern 1: Supabase MCP for Schema Changes
When AI agent needs to modify database schema:
AI Agent detects need for new field →
Uses Supabase MCP →
Generates migration →
Applies to database →
Updates Python models

### Pattern 2: Real-time Updates
Dashboard listens to Supabase real-time for live order updates:
````typescript
// Dashboard component
useEffect(() => {
  const channel = supabase
    .channel('orders')
    .on(
      'postgres_changes',
      { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'orders',
        filter: `boutique_id=eq.${boutiqueId}`
      },
      (payload) => {
        // Show notification: "New order received!"
        toast.success('New order received!')
        refetchOrders()
      }
    )
    .subscribe()

  return () => {
    supabase.removeChannel(channel)
  }
}, [boutiqueId])
````

### Pattern 3: Vector Search for Products
Using pgvector for semantic product search:
````python
async def search_products_semantic(query: str, boutique_id: str, limit: int = 5):
    # Generate embedding for query
    embedding = await generate_embedding(query)  # Using Gemini embeddings
    
    # Perform vector similarity search
    response = supabase.rpc('match_products', {
        'query_embedding': embedding,
        'match_threshold': 0.7,
        'match_count': limit,
        'boutique_id_filter': boutique_id
    }).execute()
    
    return response.data

# In Supabase, create this function:
```sql
CREATE OR REPLACE FUNCTION match_products(
  query_embedding VECTOR(1536),
  match_threshold FLOAT,
  match_count INT,
  boutique_id_filter UUID
)
RETURNS TABLE (
  id UUID,
  name TEXT,
  description TEXT,
  price DECIMAL,
  similarity FLOAT
)
LANGUAGE SQL STABLE
AS $
  SELECT
    id,
    name,
    description,
    price,
    1 - (embedding <=> query_embedding) AS similarity
  FROM products
  WHERE 
    boutique_id = boutique_id_filter
    AND is_active = true
    AND 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$;
```

Now you have complete Supabase setup with MCP integration ready!
````

---

## PROMPT 3: COMPLETE IMPLEMENTATION GUIDE
### Copy this for full development instructions
You are now implementing the complete Fashion Boutique WhatsApp AI Sales Agent platform. Follow this comprehensive guide to build the entire system.
PROJECT STRUCTURE
Create this exact folder structure:
fashion-boutique-agent/
│
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py                  # LangGraph state schema
│   │   ├── graph.py                  # Complete workflow
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── image_analysis.py     # Claude Vision image analysis
│   │       ├── product_search.py     # Semantic search
│   │       ├── size_recommendation.py # Size logic
│   │       ├── response_generation.py # Conversational responses
│   │       ├── cart_management.py    # Cart operations
│   │       ├── checkout.py           # Checkout flow
│   │       ├── payment.py            # PayLink integration
│   │       └── confirmation.py       # Order confirmation
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhooks.py               # WhatsApp + PayLink webhooks
│   │   ├── dashboard.py              # Dashboard API endpoints
│   │   ├── auth.py                   # Authentication
│   │   └── products.py               # Product management API
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase_client.py        # Supabase connection
│   │   ├── whatsapp.py               # WhatsApp client (Twilio)
│   │   ├── payments.py               # PayLink/M-Pesa
│   │   ├── product_search.py         # Search logic
│   │   ├── analytics.py              # Business metrics
│   │   └── image_processing.py       # Image utilities
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── boutique.py               # Pydantic models
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── conversation.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── helpers.py
│   │
│   ├── main.py                       # FastAPI app entry
│   ├── requirements.txt
│   └── .env
│
├── dashboard/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # Landing/login
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   └── (dashboard)/
│   │   │       ├── layout.tsx        # Dashboard layout
│   │   │       ├── page.tsx          # Overview
│   │   │       ├── products/
│   │   │       │   ├── page.tsx      # Products list
│   │   │       │   ├── [id]/page.tsx # Edit product
│   │   │       │   └── new/page.tsx  # Add product
│   │   │       ├── orders/
│   │   │       │   ├── page.tsx
│   │   │       │   └── [id]/page.tsx
│   │   │       ├── customers/page.tsx
│   │   │       ├── conversations/page.tsx
│   │   │       ├── analytics/page.tsx
│   │   │       └── settings/page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── navbar.tsx
│   │   │   │   ├── sidebar.tsx
│   │   │   │   └── footer.tsx
│   │   │   ├── products/
│   │   │   │   ├── product-card.tsx
│   │   │   │   ├── product-form.tsx
│   │   │   │   └── product-table.tsx
│   │   │   ├── orders/
│   │   │   │   ├── order-card.tsx
│   │   │   │   └── order-status.tsx
│   │   │   └── analytics/
│   │   │       ├── sales-chart.tsx
│   │   │       └── metrics-card.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── supabase/
│   │   │   │   ├── client.ts
│   │   │   │   └── server.ts
│   │   │   ├── api/
│   │   │   │   └── client.ts         # API client for backend
│   │   │   └── utils.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-boutique.ts
│   │   │   ├── use-products.ts
│   │   │   └── use-orders.ts
│   │   │
│   │   └── types/
│   │       └── index.ts              # TypeScript types
│   │
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── .env.local
│
├── supabase/
│   ├── migrations/
│   │   └── 20240101000000_initial_schema.sql
│   └── config.toml
│
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── ARCHITECTURE.md
│
├── scripts/
│   ├── seed_data.py
│   └── generate_embeddings.py
│
├── .gitignore
├── README.md
└── docker-compose.yml