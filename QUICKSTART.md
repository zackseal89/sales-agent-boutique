# 🚀 Quick Start Guide

## 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## 2. Configure Environment

Create `.env` file in `backend/` folder with your credentials:

```env
# Supabase (already configured)
SUPABASE_URL=https://xqaftsmseqzhlfclthyr.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Google Gemini (get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_google_api_key

# Twilio WhatsApp (optional for now)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

## 3. Test Supabase Connection

```bash
python test_supabase.py
```

Expected output:
```
✅ Found boutique: Nairobi Fashion House
✅ Found 3 products
✅ All tests passed!
```

## 4. Test AI Agent

```bash
python test_agent.py
```

This will test:
- Greeting flow
- Product search
- Gemini AI responses

## 5. Run Backend Server

```bash
uvicorn main:app --reload
```

Server will start at: http://localhost:8080

API docs: http://localhost:8080/docs

## 6. Test WhatsApp Webhook (Optional)

To test with real WhatsApp:

1. Set up ngrok for local tunnel:
```bash
ngrok http 8080
```

2. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

3. Configure Twilio webhook:
   - Go to Twilio Console → Messaging → WhatsApp Sandbox
   - Set webhook URL: `https://abc123.ngrok.io/webhook/whatsapp`

4. Send a message to your Twilio WhatsApp number!

## 🎯 What's Working Now

✅ Supabase database with pgvector
✅ LangGraph AI agent state machine
✅ Gemini vision for image analysis
✅ Product search (text-based)
✅ Conversational responses
✅ WhatsApp webhook handler
✅ FastAPI backend

## 🚧 Next Steps

- [ ] Add vector embeddings for semantic search
- [ ] Implement cart and checkout flow
- [ ] Add M-Pesa payment integration
- [ ] Build Next.js dashboard
- [ ] Deploy to Google Cloud Run

## 📚 Project Structure

```
backend/
├── main.py                 # FastAPI app
├── agents/
│   ├── sales_agent.py     # LangGraph orchestrator
│   └── nodes/
│       └── agent_nodes.py # Individual agent nodes
├── api/
│   └── webhooks.py        # WhatsApp webhook
├── services/
│   ├── supabase_service.py
│   ├── gemini_service.py
│   └── whatsapp_service.py
├── models/
│   └── schemas.py         # Pydantic models
└── test_*.py              # Test scripts
```
