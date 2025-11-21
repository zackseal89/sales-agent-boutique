You are building a complete WhatsApp AI Sales Agent platform for fashion boutiques in Kenya. This is a multi-tenant SaaS product where multiple fashion boutiques can have their own AI sales assistant that handles customer conversations, product recommendations, payments, and orders through WhatsApp.

## PRODUCT VISION

### What We're Building
A WhatsApp-based AI sales agent that allows fashion boutique customers to:
1. Send images of clothes they like and get similar products from the boutique
2. Browse products through natural conversation
3. Get personalized size recommendations based on purchase history
4. Add items to cart and complete purchases via M-Pesa
5. Track orders and get delivery updates

For boutique owners, this provides:
1. Automated 24/7 sales assistant
2. Dashboard to manage products, view orders, and analytics
3. Automated inventory management
4. Customer insights and purchase patterns

### Business Model
- Multi-tenant SaaS platform
- Each boutique pays $200-500/month subscription
- Or transaction-based: 2-5% of sales processed
- Target market: Fashion boutiques in Kenya and East Africa

## CORE USER FLOWS

### Flow 1: Customer Image Search Journey
1. Customer sends WhatsApp image: "Do you have this dress?"
2. AI analyzes image using Claude Vision (style, color, pattern, occasion)
3. System searches boutique's product database using semantic search
4. AI checks customer's previous orders to recommend size
5. AI responds conversationally with 3-5 matching products + images
6. Customer selects product and size
7. Added to cart with total shown
8. Customer proceeds to checkout
9. Provides delivery address
10. M-Pesa STK push sent to phone
11. Customer enters PIN to pay
12. Order confirmed, inventory updated, boutique owner notified

### Flow 2: Boutique Owner Onboarding
1. Owner signs up on web dashboard
2. Completes business profile
3. Connects WhatsApp Business number
4. Uploads product catalog (CSV or manual entry)
5. Configures M-Pesa business account
6. Sets agent personality/tone
7. Gets unique WhatsApp number or uses existing
8. Agent goes live immediately

### Flow 3: Boutique Daily Operations
1. Owner logs into dashboard
2. Views today's conversations and sales
3. Sees pending orders to fulfill
4. Updates inventory levels
5. Adds new products
6. Views analytics (top products, conversion rates, revenue)
7. Manages customer database

## TECHNICAL ARCHITECTURE

### High-Level Components
┌─────────────────────────────────────────────────┐
│         WhatsApp Business API                   │
│      (Customer conversations happen here)       │
└──────────────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (Python)                │
│  - Webhook handlers (WhatsApp, PayLink)         │
│  - API routes for dashboard                     │
│  - Background job processing                    │
└──────────────────┬──────────────────────────────┘
│
┌──────────┼──────────┐
▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌─────────────┐
│ LangGraph│ │ Supabase │ │   PayLink   │
│   Agent  │ │ Database │ │   M-Pesa    │
│          │ │ + Storage│ │   Payments  │
└─────┬────┘ └──────────┘ └─────────────┘
│
▼
┌──────────────┐
│  Gemini API  │
│ (Vision + AI)│
└──────────────┘
┌─────────────────────────────────────────────────┐
│      React Dashboard (Owner Interface)          │
│  - Product management                           │
│  - Order tracking                               │
│  - Analytics & reports                          │
│  - Settings & configuration                     │
└─────────────────────────────────────────────────┘

### State Management (LangGraph)
The AI agent is built as a state machine with these nodes:
1. **ImageAnalysis**: Analyzes customer-uploaded images using Gemini Vision
2. **ProductSearch**: Semantic search in database for matching products
3. **SizeRecommendation**: Checks purchase history for size patterns
4. **ResponseGeneration**: Creates natural conversational responses
5. **CartManagement**: Handles add/remove items, calculates totals
6. **Checkout**: Collects delivery info, prepares order
7. **Payment**: Initiates M-Pesa STK push via PayLink
8. **Confirmation**: Sends receipt, updates inventory, notifies owner

State flows between nodes based on customer responses and system events.

## KEY TECHNICAL DECISIONS

### Why LangGraph?
- Handles complex, stateful multi-turn conversations
- Built-in checkpointing for conversation persistence
- Conditional routing based on user intent
- Human-in-the-loop for payment approvals
- Easy to add new features as graph nodes

### Why Supabase?
- PostgreSQL with pgvector for semantic product search
- Built-in auth for dashboard users
- Row Level Security for multi-tenant isolation
- Storage for product images
- Real-time subscriptions for live updates
- Edge functions for serverless operations
- Automatic API generation

### Why Gemini?
- Excellent vision capabilities for fashion image analysis (Gemini 2.0 Flash)
- Strong multimodal understanding for product images
- Cost-effective with competitive pricing
- Fast response times for real-time conversations
- Native Google integration and reliability
- Long context window (1M+ tokens in Gemini 1.5 Pro)

### Why PayLink for M-Pesa?
- Simplified M-Pesa integration for Kenya
- Handles STK push (customer approves on phone)
- Webhook confirmations
- Built-in retry logic
- Local support for East African payments

## MULTI-TENANT ARCHITECTURE

### Data Isolation Strategy
Every table has `boutique_id` for complete data separation:
- Each boutique's products, orders, customers are isolated
- Row Level Security (RLS) enforces access control
- Shared infrastructure, isolated data
- One codebase serves all boutiques
│   ├── agents/
│   │   ├── nodes/          # LangGraph node implementations
│   │   ├── graph.py        # Complete workflow definition
│   │   └── state.py        # State schema
│   ├── api/
│   │   ├── webhooks.py     # WhatsApp, PayLink webhooks
│   │   ├── dashboard.py    # Dashboard API routes
│   │   └── auth.py         # Authentication
│   ├── services/
│   │   ├── whatsapp.py     # WhatsApp client
│   │   ├── payments.py     # PayLink integration
│   │   ├── products.py     # Product search logic
│   │   └── analytics.py    # Business metrics
│   ├── models/             # Pydantic models
│   └── main.py             # FastAPI app
├── dashboard/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Dashboard pages
│   │   ├── hooks/          # Custom hooks
│   │   └── lib/            # Supabase client, utils
│   └── package.json
├── supabase/
│   ├── migrations/         # Database migrations
│   └── functions/          # Edge functions
└── requirements.txt

### Error Handling
- Always wrap agent operations in try-catch
- Graceful degradation (if image analysis fails, fallback to text search)
- User-friendly error messages in WhatsApp
- Log all errors to Langfuse for debugging
- Retry logic for transient failures
- Never expose technical errors to customers

### Security
- Validate all webhook signatures (Twilio, PayLink)
- Use environment variables for secrets
- Implement rate limiting on webhooks
- Supabase RLS for data access control
- Sanitize user inputs before database queries
- HTTPS only for all endpoints
- Secure storage for API keys

### Performance
- Async/await for all I/O operations
- Database connection pooling
- Cache product embeddings
- Compress images before storage
- Lazy load conversation history
- Index frequently queried fields
- Use Supabase Edge Functions for regional performance

### Testing Strategy
- Unit tests for individual nodes
- Integration tests for complete flows
- Test with actual WhatsApp sandbox
- Mock PayLink for development
- Test multi-tenant isolation
- Load testing for scaling

### Monitoring & Observability
- Langfuse for AI agent traces
- Track: conversation quality, payment success rate, response time
- Dashboard analytics: daily sales, top products, customer acquisition
- Error tracking (Sentry or similar)
- Cost tracking for Claude API usage per boutique

## SUCCESS METRICS

### For Platform (You)
- Number of active boutiques
- Monthly Recurring Revenue (MRR)
- Conversation-to-purchase conversion rate
- Average order value
- Customer satisfaction scores
- System uptime (target: 99.9%)

### For Boutiques (Your Customers)
- Sales volume through agent vs traditional
- Time saved on customer service
- Customer retention rate
- Average response time
- Inventory turnover rate
- Customer satisfaction with AI interactions

## DEVELOPMENT PHASES

### Phase 1: MVP 
- [ ] Basic WhatsApp conversation handling
- [ ] Image analysis and product search
- [ ] Size recommendations
- [ ] M-Pesa payment integration
- [ ] Simple dashboard for one boutique
- [ ] Basic order management

### Phase 2: Multi-Tenant 
- [ ] Boutique onboarding flow
- [ ] Multi-tenant data isolation
- [ ] Product catalog management UI
- [ ] Analytics dashboard
- [ ] WhatsApp number provisioning
- [ ] Subscription/billing

### Phase 3: Advanced Features 
- [ ] Advanced product recommendations (collaborative filtering)
- [ ] Automated marketing (abandoned cart, new arrivals)
- [ ] Delivery tracking integration
- [ ] Customer loyalty program
- [ ] Inventory sync with Shopify/WooCommerce
- [ ] Multi-language support (English, Swahili)

### Phase 4: Scale & Optimize (Ongoing)
- [ ] Performance optimization
- [ ] Cost reduction (AI token usage)
- [ ] Mobile app for boutique owners
- [ ] Expansion to other East African countries
- [ ] Additional payment methods (Airtel Money, bank cards)

Now that you understand the complete system, let's proceed with the technical implementation details.