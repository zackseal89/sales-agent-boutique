# Master Agent Prompt - Usage Guide

## Overview

The **MASTER_AGENT_PROMPT.md** defines the complete behavioral and architectural guidelines for the WhatsApp AI Sales Agent production system. This guide explains how to use it effectively.

## Three Agent Roles

This system uses **three distinct agents**, each with their own responsibilities:

### 1. **Orchestrator Agent** (Main AI Agent)
**Prompt:** Use `MASTER_AGENT_PROMPT.md` sections:
- Agent Identity
- System Architecture Overview
- Core Responsibilities
- Tool Registry
- AI Reasoning Layer
- Message Processing Loop
- Agent Behavior & Personality

**Responsibilities:**
- Process WhatsApp messages from customers
- Execute tools deterministically
- Call LLM for reasoning and response generation
- Manage conversation state and memory
- Handle payments and orders

**When to use:** When implementing the backend message handler and orchestrator logic.

---

### 2. **Frontend Agent** (Dashboard Developer)
**Prompt:** Use `MASTER_AGENT_PROMPT.md` section:
- Frontend Agent Responsibilities

**Also reference:** `frontend instructions.md`

**Responsibilities:**
- Build Next.js dashboard pages
- Create modular UI components
- Implement service layer for API calls
- Never modify backend logic or Supabase schema
- Mock APIs when backend not ready

**When to use:** When developing dashboard features, UI components, or frontend integrations.

---

### 3. **Backend Agent** (Database Manager via MCP)
**Prompt:** Use `MASTER_AGENT_PROMPT.md` section:
- Backend Agent Responsibilities

**Also reference:** `Backend instructions.MD`

**Responsibilities:**
- Inspect and modify Supabase schema
- Create migrations for new tables
- Ensure RLS policies for multi-tenant isolation
- Provide rollback SQL for destructive changes
- Generate ER diagrams

**When to use:** When making database schema changes, creating migrations, or managing Supabase infrastructure.

---

## Key Behavioral Changes from LangGraph

### ❌ OLD (LangGraph Approach)
```python
# LLM decides which subagent to route to
state = graph.invoke({"messages": [user_message]})
# Unpredictable, hard to debug
```

### ✅ NEW (Tool-Centered Orchestration)
```typescript
// 1. Deterministic routing
const intent = classifyIntent(message);

// 2. LLM for reasoning only
const llmResponse = await gemini.generate({
  prompt: buildPrompt(conversation, memory, inventory),
  schema: { reply_text, actions, intent, entities }
});

// 3. Orchestrator executes tools
for (const action of llmResponse.actions) {
  await toolRegistry.execute(action.tool, action.params);
}

// 4. Send response
await twilio.sendMessage(llmResponse.reply_text);
```

---

## Quick Start: Implementing the Orchestrator

### Step 1: Message Handler
```typescript
// /backend/src/orchestrator/message-handler.ts
export async function handleWhatsAppMessage(req: Request) {
  // 1. Validate webhook
  if (!validateTwilioSignature(req)) throw new Error('Invalid signature');
  
  // 2. Extract message data
  const { From, Body, MediaUrl0 } = req.body;
  
  // 3. Identify business
  const business = await getBusinessByPhone(req.body.To);
  
  // 4. Save message to DB
  const conversation = await getOrCreateConversation(business.id, From);
  await saveMessage(conversation.id, 'customer', Body, MediaUrl0);
  
  // 5. Fetch context
  const history = await getRecentMessages(conversation.id, 8);
  const memories = await searchMemories(conversation.id, Body);
  const inventory = await getProducts(business.id);
  
  // 6. Build LLM prompt
  const prompt = buildPrompt({ history, memories, inventory, business });
  
  // 7. Call LLM (reasoning only)
  const llmResponse = await gemini.generate(prompt);
  
  // 8. Execute tools
  for (const action of llmResponse.actions) {
    await executeToolAction(action);
  }
  
  // 9. Send reply
  await twilio.sendWhatsApp(From, llmResponse.reply_text);
  
  // 10. Update memory
  await saveMemory(conversation.id, llmResponse);
}
```

### Step 2: Tool Registry
```typescript
// /backend/src/orchestrator/tool-registry.ts
export const toolRegistry = {
  get_inventory: async (params) => {
    return await supabase
      .from('products')
      .select('*')
      .eq('name', params.product_name)
      .single();
  },
  
  add_to_cart: async (params) => {
    // Update conversation metadata with cart items
    return await updateCart(params.conversation_id, params);
  },
  
  initiate_mpesa_stk: async (params) => {
    return await mpesaClient.stkPush(params);
  },
  
  // ... other tools
};

export async function executeToolAction(action: ToolAction) {
  const tool = toolRegistry[action.tool];
  if (!tool) throw new Error(`Unknown tool: ${action.tool}`);
  return await tool(action.params);
}
```

### Step 3: LLM Client (Gemini)
```typescript
// /backend/src/orchestrator/llm-client.ts
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

export async function generateResponse(prompt: string) {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
  
  const result = await model.generateContent({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: 'object',
        properties: {
          reply_text: { type: 'string' },
          actions: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                tool: { type: 'string' },
                params: { type: 'object' }
              }
            }
          },
          intent: { type: 'string' },
          entities: { type: 'object' }
        }
      }
    }
  });
  
  return JSON.parse(result.response.text());
}
```

---

## Testing the System

### 1. Unit Test Example (Tool)
```typescript
// /backend/tests/tools/product-tools.test.ts
import { toolRegistry } from '@/orchestrator/tool-registry';

describe('get_inventory', () => {
  it('should return product stock level', async () => {
    const result = await toolRegistry.get_inventory({
      product_name: 'Blue Floral Dress'
    });
    
    expect(result).toHaveProperty('stock');
    expect(result.stock).toBeGreaterThanOrEqual(0);
  });
});
```

### 2. Integration Test Example (Message Flow)
```typescript
// /backend/tests/integration/message-flow.test.ts
import { handleWhatsAppMessage } from '@/orchestrator/message-handler';

describe('WhatsApp Message Flow', () => {
  it('should process customer message end-to-end', async () => {
    const mockRequest = {
      body: {
        From: '+254712345678',
        To: '+254700000000',
        Body: 'Do you have dresses?'
      }
    };
    
    await handleWhatsAppMessage(mockRequest);
    
    // Verify message saved to DB
    const messages = await getMessages(conversationId);
    expect(messages).toHaveLength(2); // customer + agent
    
    // Verify agent response sent
    expect(twilioMock.sendMessage).toHaveBeenCalled();
  });
});
```

---

## Common Patterns

### Pattern 1: Image Analysis
```typescript
// When customer sends image
if (MediaUrl0) {
  // 1. Download and store
  const imagePath = await downloadWhatsAppImage(MediaUrl0);
  
  // 2. Analyze with Gemini Vision
  const analysis = await analyzeImage(imagePath);
  // Returns: { type, style, colors, pattern, occasion }
  
  // 3. Search similar products
  const embedding = await generateEmbedding(analysis);
  const products = await searchSimilarProducts(embedding);
  
  // 4. Include in LLM prompt
  prompt += `\nCustomer sent image: ${JSON.stringify(analysis)}`;
  prompt += `\nMatching products: ${JSON.stringify(products)}`;
}
```

### Pattern 2: Size Recommendation
```typescript
// Check purchase history for size
const customer = await getCustomerProfile(From);
if (customer.purchase_history.length > 0) {
  const sizes = customer.purchase_history.map(order => order.size);
  const mostCommonSize = mode(sizes); // e.g., "M"
  
  prompt += `\nCustomer usually buys size ${mostCommonSize}`;
}
```

### Pattern 3: Multi-Tenant Context
```typescript
// Set business context for RLS
await supabase.rpc('set_config', {
  setting: 'app.current_business',
  value: business.id
});

// All subsequent queries automatically filtered by business_id
const products = await supabase.from('products').select('*');
// Only returns products for current business
```

---

## Monitoring & Debugging

### Log Structure
```typescript
// Log every orchestrator run
await auditLog.create({
  business_id: business.id,
  conversation_id: conversation.id,
  actor: 'system',
  action: 'process_message',
  payload: {
    input: { message: Body, media: MediaUrl0 },
    tools_executed: ['analyze_image', 'search_products'],
    llm_tokens: 1234,
    response_time_ms: 850,
    status: 'success'
  }
});
```

### Error Handling
```typescript
try {
  const llmResponse = await generateResponse(prompt);
} catch (error) {
  // Log error
  await auditLog.create({
    action: 'llm_error',
    payload: { error: error.message }
  });
  
  // Fallback response
  await twilio.sendWhatsApp(From, 
    "Sorry, I'm having trouble right now. Let me connect you with a human agent."
  );
  
  // Handover to human
  await handoverToHuman(conversation.id, 'llm_timeout');
}
```

---

## Next Steps

1. **Review Implementation Plan:** See `implementation_plan.md` for deployment strategy
2. **Set Up Backend:** Implement orchestrator following patterns above
3. **Configure Supabase:** Use Backend Agent to create schema
4. **Build Dashboard:** Use Frontend Agent to create Next.js pages
5. **Test End-to-End:** Follow verification plan in implementation plan
6. **Deploy to Production:** Use deployment checklist

---

## Reference Documents

- **Master Prompt:** [MASTER_AGENT_PROMPT.md](file:///c:/Users/user/sales%20agent%20v2%20botique/MASTER_AGENT_PROMPT.md)
- **Implementation Plan:** [implementation_plan.md](file:///C:/Users/user/.gemini/antigravity/brain/9e2ee8e5-b29d-4331-9a0c-ff9211fe210f/implementation_plan.md)
- **Architecture:** [Project Overview & Architecture.MD](file:///c:/Users/user/sales%20agent%20v2%20botique/Project%20Overview%20&%20Architecture.MD)
- **Pivot Rationale:** [PIVOT INSTRUCTIONS.md](file:///c:/Users/user/sales%20agent%20v2%20botique/PIVOT%20INSTRUCTIONS.md)
- **Frontend Guidelines:** [frontend instructions.md](file:///c:/Users/user/sales%20agent%20v2%20botique/frontend%20instructions.md)
- **Backend Guidelines:** [Backend instructions.MD](file:///c:/Users/user/sales%20agent%20v2%20botique/Backend%20instructions%20.MD)

---

**Version:** 1.0  
**Last Updated:** 2025-11-22
