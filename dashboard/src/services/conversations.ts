// Conversations service layer with mock data
// Read-only - no message sending from dashboard

export interface Message {
  id: string
  conversation_id: string
  sender: "customer" | "agent"
  content: string
  media_url?: string
  media_type?: "image" | "video"
  payment_status?: "pending" | "completed" | "failed"
  created_at: string
}

export interface Conversation {
  id: string
  customer_name: string
  customer_phone: string
  last_message: string
  last_message_at: string
  unread_count: number
  status: "active" | "archived"
  created_at: string
}

export interface ConversationDetail extends Conversation {
  messages: Message[]
}

// Mock data
const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    customer_name: "Jane Wanjiku",
    customer_phone: "+254712345678",
    last_message: "Thank you! I'll make the payment now.",
    last_message_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 mins ago
    unread_count: 0,
    status: "active",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
  },
  {
    id: "conv-2",
    customer_name: "Mary Akinyi",
    customer_phone: "+254723456789",
    last_message: "Do you have this in size M?",
    last_message_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 mins ago
    unread_count: 1,
    status: "active",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
  {
    id: "conv-3",
    customer_name: "Grace Muthoni",
    customer_phone: "+254734567890",
    last_message: "Perfect! I'll take the blue one.",
    last_message_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    unread_count: 0,
    status: "active",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
]

const mockMessages: Record<string, Message[]> = {
  "conv-1": [
    {
      id: "msg-1",
      conversation_id: "conv-1",
      sender: "customer",
      content: "Hi! Do you have evening dresses?",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: "msg-2",
      conversation_id: "conv-1",
      sender: "agent",
      content: "Hello Jane! 👗 Yes, we have beautiful evening dresses. Let me show you our collection.",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2 + 1000 * 30).toISOString(),
    },
    {
      id: "msg-3",
      conversation_id: "conv-1",
      sender: "agent",
      content: "Here's our Elegant Evening Gown - KES 12,500. Available in Black, Red, and Navy.",
      media_url: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400",
      media_type: "image",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2 + 1000 * 45).toISOString(),
    },
    {
      id: "msg-4",
      conversation_id: "conv-1",
      sender: "customer",
      content: "I love the black one! Do you have size M?",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 1.5).toISOString(),
    },
    {
      id: "msg-5",
      conversation_id: "conv-1",
      sender: "agent",
      content: "Yes! The black evening gown in size M is in stock. Would you like to proceed with the order?",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 1.5 + 1000 * 20).toISOString(),
    },
    {
      id: "msg-6",
      conversation_id: "conv-1",
      sender: "customer",
      content: "Yes please!",
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    },
    {
      id: "msg-7",
      conversation_id: "conv-1",
      sender: "agent",
      content: "Great! I'll send you the M-Pesa payment request for KES 12,500. Please complete the payment to confirm your order.",
      payment_status: "completed",
      created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    },
    {
      id: "msg-8",
      conversation_id: "conv-1",
      sender: "customer",
      content: "Thank you! I'll make the payment now.",
      created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    },
  ],
  "conv-2": [
    {
      id: "msg-9",
      conversation_id: "conv-2",
      sender: "customer",
      content: "Hello",
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    },
    {
      id: "msg-10",
      conversation_id: "conv-2",
      sender: "agent",
      content: "Hi Mary! 👋 Welcome to our boutique. How can I help you today?",
      created_at: new Date(Date.now() - 1000 * 60 * 60 + 1000 * 15).toISOString(),
    },
    {
      id: "msg-11",
      conversation_id: "conv-2",
      sender: "customer",
      content: "",
      media_url: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
      media_type: "image",
      created_at: new Date(Date.now() - 1000 * 60 * 50).toISOString(),
    },
    {
      id: "msg-12",
      conversation_id: "conv-2",
      sender: "agent",
      content: "I can see you're interested in a floral dress! We have a similar Floral Summer Dress - KES 4,500. Available in Blue, Pink, and White. Sizes S, M, L, XL.",
      created_at: new Date(Date.now() - 1000 * 60 * 50 + 1000 * 30).toISOString(),
    },
    {
      id: "msg-13",
      conversation_id: "conv-2",
      sender: "customer",
      content: "Do you have this in size M?",
      created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    },
  ],
  "conv-3": [
    {
      id: "msg-14",
      conversation_id: "conv-3",
      sender: "customer",
      content: "Do you have denim jackets?",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    },
    {
      id: "msg-15",
      conversation_id: "conv-3",
      sender: "agent",
      content: "Yes! We have a Classic Denim Jacket - KES 6,800. Available in Blue and Black. Sizes S, M, L.",
      media_url: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
      media_type: "image",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 3 + 1000 * 25).toISOString(),
    },
    {
      id: "msg-16",
      conversation_id: "conv-3",
      sender: "customer",
      content: "Perfect! I'll take the blue one.",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
  ],
}

// Toggle between mock and real API
const USE_MOCK_API = true

// Service functions
export async function getConversations(): Promise<Conversation[]> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockConversations
  }

  const response = await fetch("/api/conversations")
  if (!response.ok) throw new Error("Failed to fetch conversations")
  return response.json()
}

export async function getConversation(id: string): Promise<ConversationDetail | null> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    const conversation = mockConversations.find((c) => c.id === id)
    if (!conversation) return null

    return {
      ...conversation,
      messages: mockMessages[id] || [],
    }
  }

  const response = await fetch(`/api/conversations/${id}`)
  if (!response.ok) throw new Error("Failed to fetch conversation")
  return response.json()
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return mockMessages[conversationId] || []
  }

  const response = await fetch(`/api/conversations/${conversationId}/messages`)
  if (!response.ok) throw new Error("Failed to fetch messages")
  return response.json()
}
