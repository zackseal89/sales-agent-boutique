// Customers service layer with mock data

export interface CustomerOrder {
  id: string
  order_number: string
  total: number
  status: string
  created_at: string
}

export interface Customer {
  id: string
  name: string
  phone: string
  email?: string
  total_orders: number
  total_spent: number
  last_interaction: string
  created_at: string
}

export interface CustomerDetail extends Customer {
  orders: CustomerOrder[]
  preferences: {
    favorite_categories?: string[]
    preferred_sizes?: string[]
    preferred_colors?: string[]
  }
  notes?: string
}

// Mock data
const mockCustomers: Customer[] = [
  {
    id: "cust-1",
    name: "Jane Wanjiku",
    phone: "+254712345678",
    email: "jane.wanjiku@example.com",
    total_orders: 3,
    total_spent: 28900,
    last_interaction: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
  },
  {
    id: "cust-2",
    name: "Mary Akinyi",
    phone: "+254723456789",
    total_orders: 1,
    total_spent: 4500,
    last_interaction: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
  },
  {
    id: "cust-3",
    name: "Grace Muthoni",
    phone: "+254734567890",
    total_orders: 2,
    total_spent: 13900,
    last_interaction: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
  },
  {
    id: "cust-4",
    name: "Sarah Njeri",
    phone: "+254745678901",
    email: "sarah.njeri@example.com",
    total_orders: 4,
    total_spent: 35200,
    last_interaction: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 45).toISOString(),
  },
  {
    id: "cust-5",
    name: "Lucy Wambui",
    phone: "+254756789012",
    total_orders: 2,
    total_spent: 26400,
    last_interaction: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString(),
  },
]

const mockCustomerDetails: Record<string, CustomerDetail> = {
  "cust-1": {
    ...mockCustomers[0],
    orders: [
      {
        id: "order-1",
        order_number: "ORD-2024-001",
        total: 12800,
        status: "confirmed",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      },
      {
        id: "order-5",
        order_number: "ORD-2024-005",
        total: 9300,
        status: "delivered",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
      },
      {
        id: "order-6",
        order_number: "ORD-2024-006",
        total: 6800,
        status: "delivered",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString(),
      },
    ],
    preferences: {
      favorite_categories: ["Dresses", "Formal Wear"],
      preferred_sizes: ["M"],
      preferred_colors: ["Black", "Navy", "Red"],
    },
    notes: "Prefers formal and elegant styles. Size M fits perfectly.",
  },
  "cust-2": {
    ...mockCustomers[1],
    orders: [
      {
        id: "order-7",
        order_number: "ORD-2024-007",
        total: 4500,
        status: "pending",
        created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      },
    ],
    preferences: {
      favorite_categories: ["Dresses"],
      preferred_sizes: ["M"],
      preferred_colors: ["Blue", "Pink"],
    },
  },
  "cust-3": {
    ...mockCustomers[2],
    orders: [
      {
        id: "order-2",
        order_number: "ORD-2024-002",
        total: 7100,
        status: "pending",
        created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      },
      {
        id: "order-8",
        order_number: "ORD-2024-008",
        total: 6800,
        status: "delivered",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
      },
    ],
    preferences: {
      favorite_categories: ["Jackets", "Casual Wear"],
      preferred_sizes: ["M"],
      preferred_colors: ["Blue", "Black"],
    },
  },
  "cust-4": {
    ...mockCustomers[3],
    orders: [
      {
        id: "order-3",
        order_number: "ORD-2024-003",
        total: 9300,
        status: "shipped",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      },
    ],
    preferences: {
      favorite_categories: ["Dresses", "Casual Wear"],
      preferred_sizes: ["S", "M"],
      preferred_colors: ["Blue", "White", "Pink"],
    },
    notes: "Frequently orders multiple items. Prefers casual styles.",
  },
  "cust-5": {
    ...mockCustomers[4],
    orders: [
      {
        id: "order-4",
        order_number: "ORD-2024-004",
        total: 19600,
        status: "delivered",
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
      },
    ],
    preferences: {
      favorite_categories: ["Dresses", "Jackets"],
      preferred_sizes: ["L", "M"],
      preferred_colors: ["Red", "Black"],
    },
  },
}

// Toggle between mock and real API
const USE_MOCK_API = true

// Service functions
export async function getCustomers(): Promise<Customer[]> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockCustomers
  }

  const response = await fetch("/api/customers")
  if (!response.ok) throw new Error("Failed to fetch customers")
  return response.json()
}

export async function getCustomer(id: string): Promise<CustomerDetail | null> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return mockCustomerDetails[id] || null
  }

  const response = await fetch(`/api/customers/${id}`)
  if (!response.ok) throw new Error("Failed to fetch customer")
  return response.json()
}

export async function searchCustomers(query: string): Promise<Customer[]> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    const lowerQuery = query.toLowerCase()
    return mockCustomers.filter(
      (c) =>
        c.name.toLowerCase().includes(lowerQuery) ||
        c.phone.includes(query) ||
        c.email?.toLowerCase().includes(lowerQuery)
    )
  }

  const response = await fetch(`/api/customers/search?q=${encodeURIComponent(query)}`)
  if (!response.ok) throw new Error("Failed to search customers")
  return response.json()
}
