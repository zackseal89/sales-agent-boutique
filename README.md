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
- **AI Agent**: LangGraph + Google Gemini 2.0 Flash
- **Database**: Supabase (PostgreSQL + pgvector)
- **Frontend**: Next.js 14 + TypeScript
- **Payments**: PayLink M-Pesa
- **Messaging**: Twilio WhatsApp Business API

## 📁 Project Structure

```
fashion-boutique-agent/
├── backend/              # FastAPI backend
│   ├── agents/          # LangGraph agent logic
│   ├── api/             # API routes & webhooks
│   ├── services/        # External service integrations
│   ├── models/          # Pydantic models
│   └── utils/           # Helper functions
├── dashboard/           # Next.js dashboard
├── supabase/           # Database migrations
└── scripts/            # Utility scripts
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
cp .env.example .env  # Configure your environment variables
uvicorn main:app --reload
```

### Dashboard Setup

```bash
cd dashboard
npm install
cp .env.local.example .env.local  # Configure your environment variables
npm run dev
```

## 📚 Documentation

See the following guides for detailed information:

- [Project Overview & Architecture](./Project%20Overview%20&%20Architecture.MD)
- [Technical Stack & Supabase Setup](./Technical%20Stack%20&%20Supabase%20Setup.MD)
- [Master Implementation Guide](./Master%20Implementation%20Guide.MD)
- [Visual Architecture Overview](./.gemini/antigravity/brain/21f26c1a-88a3-48a6-b53e-2da4536e53e0/architecture_visual_overview.md)

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
