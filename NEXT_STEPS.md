# 🚀 NEXT ACTION STEPS - Production Implementation Roadmap

## 📍 Current Status

**What We Have:**
- ✅ Existing Python/FastAPI backend with LangGraph
- ✅ Supabase database (Postgres + pgvector)
- ✅ Twilio WhatsApp integration
- ✅ Google Gemini 2.0 Flash integration
- ✅ Basic tools (product search, cart, checkout, payments)
- ✅ Master Agent Prompt documentation
- ✅ Implementation plan

**What We Need:**
- ❌ Migrate from LangGraph to tool-centered orchestration
- ❌ Implement deterministic message handler
- ❌ Restructure tool execution
- ❌ Build Next.js dashboard
- ❌ Production deployment

---

## 🎯 PHASE 1: BACKEND MIGRATION (Priority: CRITICAL)
**Timeline: 3-5 days**

### Step 1.1: Create New Orchestrator Structure
**What to do:**
```bash
cd backend
mkdir -p orchestrator
touch orchestrator/__init__.py
touch orchestrator/message_handler.py
touch orchestrator/tool_registry.py
touch orchestrator/context_builder.py
touch orchestrator/llm_client.py
```

**Files to create:**

#### `orchestrator/message_handler.py`
Main entry point for WhatsApp messages. Replaces LangGraph routing.

**Key functions:**
- `handle_whatsapp_message(request)` - Process incoming webhook
- `classify_intent(message)` - Deterministic intent classification
- `execute_workflow(intent, context)` - Route to appropriate tools

#### `orchestrator/tool_registry.py`
Central registry for all tools (replaces LangGraph nodes).

**Migrate existing tools from:**
- `agents/tools.py` → `orchestrator/tool_registry.py`
- Keep existing tool logic, just change how they're called

#### `orchestrator/context_builder.py`
Build LLM prompts with conversation history + memory.

**Key functions:**
- `build_prompt(conversation, memory, inventory, business)` - Construct LLM input
- `fetch_conversation_history(conversation_id, limit=8)` - Get recent messages
- `fetch_relevant_memories(conversation_id, query)` - Vector search

#### `orchestrator/llm_client.py`
Gemini API wrapper (reasoning only, not routing).

**Key functions:**
- `generate_response(prompt)` - Call Gemini with structured output
- Returns: `{ reply_text, actions, intent, entities }`

---

### Step 1.2: Update Webhook Handler
**File:** `api/webhooks.py`

**Current flow (LangGraph):**
```python
# OLD
from agents.sales_agent import run_agent
result = await run_agent(...)  # LangGraph decides everything
```

**New flow (Tool-Centered):**
```python
# NEW
from orchestrator.message_handler import handle_whatsapp_message
result = await handle_whatsapp_message(request)  # Deterministic
```

**Action:**
1. Keep existing webhook validation (Twilio signature)
2. Replace `run_agent()` call with `handle_whatsapp_message()`
3. Keep existing response sending logic

---

### Step 1.3: Remove LangGraph Dependencies
**File:** `requirements.txt`

**Remove:**
```
langchain>=0.1.0
langchain-google-genai
langgraph
langsmith
```

**Keep:**
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
google-generativeai  # For Gemini
supabase
twilio
httpx
```

**Action:**
```bash
pip uninstall langchain langgraph langsmith langchain-google-genai
pip install -r requirements.txt
```

---

### Step 1.4: Migrate Existing Tools
**Current location:** `agents/tools.py` (17,986 bytes - lots of tools!)

**Action:**
1. **Keep the tool logic** - Don't rewrite, just reorganize
2. **Create tool registry pattern:**

```python
# orchestrator/tool_registry.py
from typing import Dict, Callable, Any

# Import existing tool functions
from services.supabase_service import supabase_service
from services.gemini_service import gemini_service
from services.paylink_service import paylink_service

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            # Product tools
            "get_inventory": self.get_inventory,
            "search_products": self.search_products,
            "search_similar_products": self.search_similar_products,
            
            # Cart tools
            "add_to_cart": self.add_to_cart,
            "remove_from_cart": self.remove_from_cart,
            "get_cart": self.get_cart,
            
            # Payment tools
            "initiate_mpesa_stk": self.initiate_mpesa_stk,
            "check_payment_status": self.check_payment_status,
            
            # Image tools
            "analyze_image": self.analyze_image,
            
            # Customer tools
            "get_customer_profile": self.get_customer_profile,
        }
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_func = self.tools[tool_name]
        return await tool_func(**params)
    
    # Copy existing tool implementations from agents/tools.py
    async def get_inventory(self, product_name: str):
        # Existing logic from tools.py
        pass
    
    async def search_products(self, query: str, filters: dict = None):
        # Existing logic from tools.py
        pass
    
    # ... etc for all tools
```

---

### Step 1.5: Test Migration
**Create:** `test_orchestrator.py`

```python
import pytest
from orchestrator.message_handler import handle_whatsapp_message

@pytest.mark.asyncio
async def test_text_message():
    """Test basic text message processing"""
    mock_request = {
        "From": "+254712345678",
        "To": "+254700000000",
        "Body": "Do you have dresses?"
    }
    
    result = await handle_whatsapp_message(mock_request)
    
    assert result["response"]
    assert isinstance(result["response"], str)

@pytest.mark.asyncio
async def test_image_message():
    """Test image message processing"""
    mock_request = {
        "From": "+254712345678",
        "To": "+254700000000",
        "Body": "Do you have this?",
        "MediaUrl0": "https://example.com/image.jpg"
    }
    
    result = await handle_whatsapp_message(mock_request)
    
    assert result["response"]
    # Should mention products found
```

**Run tests:**
```bash
pytest test_orchestrator.py -v
```

---

## 🎯 PHASE 2: DATABASE VERIFICATION (Priority: HIGH)
**Timeline: 1 day**

### Step 2.1: Verify Supabase Schema
**Use Backend Agent (MCP) to check:**

```sql
-- Check existing tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Verify required tables exist:
-- ✓ businesses
-- ✓ conversations
-- ✓ messages
-- ✓ products
-- ✓ orders
-- ✓ agent_memories (if not, create)
```

### Step 2.2: Add Missing Tables (if needed)
**Backend Agent will create:**

```sql
-- Agent memories for long-term context
CREATE TABLE IF NOT EXISTS agent_memories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid REFERENCES conversations(id),
  summary text NOT NULL,
  embedding vector(1536),
  created_at timestamptz DEFAULT now()
);

CREATE INDEX ON agent_memories USING ivfflat (embedding vector_cosine_ops);
```

### Step 2.3: Verify RLS Policies
**Backend Agent will check:**
- Multi-tenant isolation via `business_id`
- Row Level Security enabled on all tables
- Policies enforce tenant boundaries

---

## 🎯 PHASE 3: FRONTEND DASHBOARD (Priority: MEDIUM)
**Timeline: 5-7 days**

### Step 3.1: Initialize Next.js Project
```bash
cd ..  # Back to project root
npx create-next-app@latest dashboard --typescript --tailwind --app
cd dashboard
npm install @supabase/supabase-js
npm install shadcn-ui
npx shadcn-ui@latest init
```

### Step 3.2: Create Dashboard Structure
```bash
mkdir -p app/dashboard/{overview,conversations,products,orders,customers,settings}
mkdir -p src/{components,services,lib}
```

### Step 3.3: Build Core Pages (Following Frontend Instructions)
**Priority order:**
1. **Overview** - Analytics cards (sales, conversations, orders)
2. **Products** - CRUD interface for catalog
3. **Conversations** - Read-only WhatsApp viewer
4. **Orders** - Order tracking
5. **Customers** - Customer database
6. **Settings** - Business config

**Use Frontend Agent for this** - follows `frontend instructions.md`

---

## 🎯 PHASE 4: TESTING & VALIDATION (Priority: CRITICAL)
**Timeline: 2-3 days**

### Step 4.1: Unit Tests
```bash
cd backend
pytest tests/tools/ -v  # Test all tools
pytest tests/orchestrator/ -v  # Test message handler
```

### Step 4.2: Integration Tests
```bash
pytest tests/integration/ -v  # Test complete flows
```

### Step 4.3: Manual WhatsApp Testing
1. Send test message to Twilio sandbox
2. Verify agent responds correctly
3. Send image, verify analysis works
4. Complete full purchase flow
5. Verify M-Pesa payment (test mode)

---

## 🎯 PHASE 5: DEPLOYMENT (Priority: HIGH)
**Timeline: 2 days**

### Step 5.1: Deploy Backend to Google Cloud Run
```bash
cd backend
gcloud run deploy fashion-boutique-api \
  --source . \
  --region africa-south1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env | grep -v '^#' | xargs)"
```

### Step 5.2: Deploy Frontend to Vercel
```bash
cd dashboard
vercel --prod
```

### Step 5.3: Update Twilio Webhook URL
Point Twilio webhook to Cloud Run URL:
```
https://fashion-boutique-api-xxx.a.run.app/webhook/whatsapp
```

---

## 📋 IMMEDIATE NEXT STEPS (Start Today)

### ✅ Step 1: Create Orchestrator Structure (30 mins)
```bash
cd backend
mkdir orchestrator
# Create files as outlined in Phase 1, Step 1.1
```

### ✅ Step 2: Implement Message Handler (2-3 hours)
**File:** `orchestrator/message_handler.py`

**Start with this template:**
```python
from fastapi import Request
from typing import Dict, Any
from services.supabase_service import supabase_service
from orchestrator.tool_registry import ToolRegistry
from orchestrator.llm_client import generate_response
from orchestrator.context_builder import build_prompt

async def handle_whatsapp_message(request: Request) -> Dict[str, Any]:
    """Main orchestrator - replaces LangGraph"""
    
    # 1. Extract message data
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    body = request.form.get("Body", "")
    media_url = request.form.get("MediaUrl0")
    
    # 2. Identify business (from Twilio number)
    business = await get_business_by_phone(to_number)
    
    # 3. Get/create conversation
    conversation = await get_or_create_conversation(
        business.id, from_number
    )
    
    # 4. Save customer message
    await save_message(conversation.id, "customer", body, media_url)
    
    # 5. Fetch context
    history = await get_recent_messages(conversation.id, limit=8)
    memories = await search_memories(conversation.id, body)
    inventory = await get_products(business.id)
    
    # 6. Build LLM prompt
    prompt = build_prompt({
        "history": history,
        "memories": memories,
        "inventory": inventory,
        "business": business,
        "current_message": body,
        "has_image": bool(media_url)
    })
    
    # 7. Call LLM (reasoning only)
    llm_response = await generate_response(prompt)
    # Returns: { reply_text, actions, intent, entities }
    
    # 8. Execute tools
    tool_registry = ToolRegistry()
    for action in llm_response.get("actions", []):
        await tool_registry.execute(action["tool"], action["params"])
    
    # 9. Save agent response
    await save_message(
        conversation.id, 
        "agent", 
        llm_response["reply_text"]
    )
    
    # 10. Return response (webhook handler will send via Twilio)
    return {
        "response": llm_response["reply_text"],
        "images": [],  # Add product images if needed
        "intent": llm_response["intent"]
    }
```

### ✅ Step 3: Test Locally (1 hour)
```bash
# Start backend
cd backend
uvicorn main:app --reload

# In another terminal, test webhook
curl -X POST http://localhost:8080/webhook/whatsapp \
  -d "From=+254712345678" \
  -d "To=+254700000000" \
  -d "Body=Do you have dresses?"
```

### ✅ Step 4: Verify Database (30 mins)
Use Supabase MCP to check schema and create missing tables.

---

## 🎯 SUCCESS CRITERIA

**Week 1 (Backend Migration):**
- ✅ Orchestrator implemented
- ✅ LangGraph removed
- ✅ All tools migrated
- ✅ Tests passing
- ✅ Local testing successful

**Week 2 (Frontend + Testing):**
- ✅ Dashboard pages built
- ✅ Integration tests passing
- ✅ Manual WhatsApp testing successful

**Week 3 (Deployment):**
- ✅ Backend deployed to Cloud Run
- ✅ Frontend deployed to Vercel
- ✅ Production testing complete
- ✅ First boutique onboarded

---

## 📞 DECISION POINTS

**Question 1:** Do you want to:
- **A)** Start with backend migration (recommended)
- **B)** Start with frontend dashboard
- **C)** Do both in parallel (requires coordination)

**Question 2:** Current backend has existing tools in `agents/tools.py`. Do you want to:
- **A)** Keep existing tool logic, just reorganize (faster)
- **B)** Rewrite tools from scratch (cleaner but slower)

**Question 3:** Timeline preference:
- **A)** Fast migration (2 weeks, minimal changes)
- **B)** Thorough migration (3-4 weeks, comprehensive testing)

---

## 🚀 RECOMMENDED STARTING POINT

**I recommend starting with:**

1. **Backend migration** (Phase 1) - Most critical
2. **Create orchestrator structure** (30 mins)
3. **Implement message handler** (2-3 hours)
4. **Test locally** (1 hour)

**Total time to first working version: ~4-5 hours**

Then we can iterate and add dashboard, testing, deployment.

**Ready to start? Which phase would you like to begin with?**
