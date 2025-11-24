# Fashion Boutique WhatsApp AI Sales Agent

A multi-tenant SaaS platform that enables fashion boutiques in Kenya and East Africa to automate their sales through AI-powered WhatsApp agents.

## 🚀 Features

- **Image-First Shopping**: Customers send photos, AI finds similar products
- **Personalized Recommendations**: Size suggestions based on purchase history
- **M-Pesa Payments**: Seamless STK push integration
- **Multi-Tenant**: One platform serves hundreds of boutiques
- **Serverless**: Google Cloud Run for auto-scaling and cost efficiency

## 🏗️ Architecture

- **Backend**: FastAPI + Python 3.11 (serverless on Google Cloud Run)
- **AI Agent**: BoutiqueAIAgent with Model Context Protocol (MCP) + Google Gemini
- **Database**: Supabase (PostgreSQL + pgvector)
- **Frontend**: Next.js 14 + TypeScript
- **Payments**: PayLink M-Pesa
- **Messaging**: Twilio WhatsApp Business API

## 📁 Project Structure

```
fashion-boutique-agent/
├── backend/              # FastAPI backend
│   ├── agents/          # AI agent logic (BoutiqueAIAgent)
│   ├── api/             # API routes & webhooks
│   ├── services/        # External service integrations (Supabase, Twilio, MCP)
│   ├── models/          # Pydantic models
│   └── utils/           # Helper functions (e.g., AI model wrappers)
├── dashboard/           # Next.js dashboard
├── supabase/            # Database migrations
└── tests/               # Test files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- Google Cloud account (for Gemini API)
- Twilio account (for WhatsApp)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Create a .env file and add your environment variables:
# SUPABASE_URL=...
# SUPABASE_SERVICE_KEY=...
# SUPABASE_ANON_KEY=...
# GOOGLE_API_KEY=...
# TWILIO_ACCOUNT_SID=...
# TWILIO_AUTH_TOKEN=...
# TWILIO_WHATSAPP_NUMBER=...
python -m uvicorn backend.main:app --reload --port 8000
```

#### 🔧 Development Mode: Mock LLM

For development and testing without relying on the Gemini API, you can enable the mock LLM mode:

1. **Enable Mock Mode**: Add to your `.env` file:
   ```env
   USE_MOCK_LLM=true
   ```

2. **What It Does**: 
   - Bypasses the real Gemini API call
   - Returns a static JSON response for testing
   - Useful for testing orchestrator logic, tool execution, and WhatsApp flow without LLM dependency

3. **When to Use**:
   - Testing the WhatsApp webhook integration
   - Developing frontend dashboard components
   - Writing unit tests for orchestrator logic
   - Debugging tool execution without LLM variability
   - Working offline or when Gemini API is unavailable

4. **Disable Mock Mode**: Set `USE_MOCK_LLM=false` or remove the variable to use the real Gemini API

5. **Run Tests**:
   ```bash
   python -m pytest backend/tests
   ```

### Frontend Setup

```bash
cd dashboard
npm install
# Create a .env.local file and add your environment variables:
# NEXT_PUBLIC_SUPABASE_URL=...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=...
npm run dev
```

## 📚 Documentation

See the following guides for detailed information:

- [Project Overview & Architecture](./Project%20Overview%20&%20Architecture.MD)
- [Technical Stack & Supabase Setup](./Technical%20Stack%20&%20Supabase%20Setup.MD)
- [Master Implementation Guide](./Master%20Implementation%20Guide.MD)
- [Master Agent Prompt](./MASTER_AGENT_PROMPT.md)

## 🌍 Deployment

- **Backend**: Google Cloud Run (africa-south1 region)
- **Frontend**: Vercel
- **Database**: Supabase (managed PostgreSQL)

## 💰 Business Model

- Freemium: First 100 conversations free
- Starter Plan: $200/month
- Growth Plan: $400/month
- Enterprise: Custom pricing

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.
