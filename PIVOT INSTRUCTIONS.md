Pivot Instructions: From LangGraph → Deterministic Tool-Centered AI Agent
1️⃣ Core Mindset Shift
Old Approach	New Approach
LMM decides routing → unpredictable	Deterministic orchestrator handles routing; LLM only for reasoning
LangGraph → research-focused	Custom agent orchestrator → production SaaS
Probabilistic, creative sub-agent calls	Event-driven, tool-first workflow
Ngrok-dependent dev testing	HTTPS deployed backend; Supabase + Twilio + Vercel
LLM triggers APIs directly	Backend executes tools after structured LLM reasoning

Think of the agent as a junior digital sales rep: consistent, predictable, and business-focused.

2️⃣ Architectural Layers (New)

1. Transport Layer

Twilio WhatsApp webhook → /api/twilio/webhook

Save raw message in Supabase

No ngrok in production

2. Memory & Data Layer

Supabase (Postgres + pgvector)

Stores:

Conversations

Messages

Vector embeddings (memory & product knowledge)

Customer profiles

Use pgvector for semantic search & product similarity

3. Agent Orchestrator Layer

Deterministic logic (no LLM routing)

Steps:

Classify intent

Fetch conversation history (last 8 messages)

Retrieve relevant memory vectors

Fetch business data (inventory, pricing, settings)

Dispatch tool calls (inventory, payments, orders, handover)

Send structured prompt to LLM for reasoning and response generation

Execute tool actions

Send reply via Twilio

Include fallbacks if a tool fails

4. Tool Layer (Deterministic Functions)

Tool	Responsibility
get_inventory(product_name)	Check stock
create_order(data)	Generate order in Supabase
initiate_mpesa_stk(phone, amount)	Execute payment
search_similar_products(image_embedding)	Return similar product suggestions
handover_to_human()	Trigger human agent takeover

5. AI Reasoning Layer

Only for understanding intent, extracting entities, deciding business actions, and generating text responses

Must not trigger APIs or control routing

6. Dashboard Layer

Next.js frontend

Business-facing:

Monitor conversations

Manage products

See analytics

Intervene in conversations

Safe integration mode (modular, non-destructive)

7. Background Workers

BullMQ + Redis for async tool execution (payments, embedding updates, long-running tasks)

3️⃣ Message Processing Loop (Deterministic)
User sends message →
Twilio webhook (/api/twilio/webhook) →
Save raw message →
Fetch last 8 conversation messages →
Fetch relevant memory vectors →
Fetch business data & inventory →
Build structured LLM prompt →
LLM returns structured JSON:
    reply_text
    actions (tool calls)
Backend executes tool actions →
Send final reply via Twilio →
Update memory, metrics, logs


Key principle: LLM cannot control state, send messages, or trigger APIs directly.

4️⃣ Image Handling Flow

Download image from Twilio

Store in Supabase Storage

Generate:

OCR text

Caption

Visual embedding

Search product embeddings in Supabase

Feed results into LLM

Generate contextual recommendations

5️⃣ Supabase Table Setup (Minimal for Pivot)
Table	Notes
businesses	id, name, phone, settings jsonb
agents	id, business_id fk, config jsonb
conversations	id, business_id fk, customer_phone, status, metadata jsonb
messages	id, conversation_id fk, role, content, attachments jsonb
products	id, business_id fk, sku, name, description, price, stock, attrs jsonb
orders	id, conversation_id fk, business_id, amount, currency, status, mpesa_reference
agent_memories	id, conversation_id, summary, vector
audit_logs	id, actor, action, payload jsonb

Include indexes on conversation_id, business_id, created_at

Use pgvector for embeddings

6️⃣ Stack Setup (Mandatory)
Layer	Stack
Backend	Node.js + TypeScript (Fastify or Express)
Database	Supabase (Postgres + pgvector + Storage + Auth)
Frontend	Next.js
Messaging	Twilio WhatsApp API
Payments	Safaricom M-Pesa STK Push
AI / LLM	OpenAI / Claude / hosted LLM w/ function calling
Realtime Updates	Supabase Realtime / WebSockets
Background Workers	BullMQ + Redis
7️⃣ Development Priorities

Implement deterministic Agent Orchestrator

Define tool registry (inventory, orders, payments, handover)

Integrate LLM reasoning layer safely

Build Supabase schema (conversations, messages, products, orders, embeddings)

Implement WhatsApp webhook and Twilio integration

Build Next.js Dashboard (safe integration mode)

Add vector search + memory retrieval

Implement fallbacks & metrics logging

8️⃣ Rules for the New AI Agent

Deterministic routing — no LLM routing

LLM used only for reasoning and response text

Tools execute all side effects

Conversation memory always retrieved and updated

Agent behaves like a junior sales rep:

Ask clarifying questions if needed

Suggest 2–3 options max

Use Kenyan English / Sheng optional

Prioritize conversions, clarity, brevity

9️⃣ Action Plan for Pivot

Deprecate LangGraph → archive for reference

Deploy HTTPS backend (Express/Fastify)

Build deterministic agent orchestrator

Implement Supabase tables + pgvector embeddings

Replace ngrok with proper deployment

Integrate Twilio webhook → backend → orchestrator → tools → LLM

Build Next.js dashboard in modular, safe mode

Test conversation flow with real WhatsApp sandbox

Add image handling and product recommendation logic

Add metrics, logs, memory persistence, and verification checks