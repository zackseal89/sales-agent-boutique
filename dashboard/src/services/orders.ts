// Orders service layer with mock data

export interface OrderItem {
  id: string
  product_id: string
  product_name: string
  product_image: string
  quantity: number
  price: number
  size?: string
  color?: string
}

export interface Order {
  id: string
  order_number: string
  customer_name: string
  customer_phone: string
  items: OrderItem[]
  subtotal: number
  delivery_fee: number
  total: number
  payment_status: "pending" | "completed" | "failed"
  payment_method: "mpesa"
  mpesa_transaction_id?: string
  order_status: "pending" | "confirmed" | "shipped" | "delivered" | "cancelled"
  delivery_address: string
  delivery_notes?: string
  created_at: string
  updated_at: string
}

// Mock data
const mockOrders: Order[] = [
  {
    id: "order-1",
    order_number: "ORD-2024-001",
    customer_name: "Jane Wanjiku",
    customer_phone: "+254712345678",
    items: [
      {
        id: "item-1",
        product_id: "3",
        product_name: "Elegant Evening Gown",
        product_image: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400",
        quantity: 1,
        price: 12500,
        size: "M",
        color: "Black",
      },
    ],
    subtotal: 12500,
    delivery_fee: 300,
    total: 12800,
    payment_status: "completed",
    payment_method: "mpesa",
    mpesa_transaction_id: "QGH7K2M9XY",
    order_status: "confirmed",
    delivery_address: "Kilimani, Nairobi",
    delivery_notes: "Call when you arrive",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: "order-2",
    order_number: "ORD-2024-002",
    customer_name: "Grace Muthoni",
    customer_phone: "+254734567890",
    items: [
      {
        id: "item-2",
        product_id: "2",
        product_name: "Classic Denim Jacket",
        product_image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
        quantity: 1,
        price: 6800,
        size: "M",
        color: "Blue",
      },
    ],
    subtotal: 6800,
    delivery_fee: 300,
    total: 7100,
    payment_status: "pending",
    payment_method: "mpesa",
    order_status: "pending",
    delivery_address: "Westlands, Nairobi",
    created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  },
  {
    id: "order-3",
    order_number: "ORD-2024-003",
    customer_name: "Sarah Njeri",
    customer_phone: "+254745678901",
    items: [
      {
        id: "item-3",
        product_id: "1",
        product_name: "Floral Summer Dress",
        product_image: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
        quantity: 2,
        price: 4500,
        size: "S",
        color: "Blue",
      },
    ],
    subtotal: 9000,
    delivery_fee: 300,
    total: 9300,
    payment_status: "completed",
    payment_method: "mpesa",
    mpesa_transaction_id: "QGH7K2M9AB",
    order_status: "shipped",
    delivery_address: "Karen, Nairobi",
    delivery_notes: "Leave at gate",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "order-4",
    order_number: "ORD-2024-004",
    customer_name: "Lucy Wambui",
    customer_phone: "+254756789012",
    items: [
      {
        id: "item-4",
        product_id: "3",
        product_name: "Elegant Evening Gown",
        product_image: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400",
        quantity: 1,
        price: 12500,
        size: "L",
        color: "Red",
      },
      {
        id: "item-5",
        product_id: "2",
        product_name: "Classic Denim Jacket",
        product_image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
        quantity: 1,
        price: 6800,
        size: "M",
        color: "Black",
      },
    ],
    subtotal: 19300,
    delivery_fee: 300,
    total: 19600,
    payment_status: "completed",
    payment_method: "mpesa",
    mpesa_transaction_id: "QGH7K2M9CD",
    order_status: "delivered",
    delivery_address: "Lavington, Nairobi",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
]

// Toggle between mock and real API
const USE_MOCK_API = true

// Service functions
export async function getOrders(): Promise<Order[]> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockOrders
  }

  const response = await fetch("/api/orders")
  if (!response.ok) throw new Error("Failed to fetch orders")
  return response.json()
}

export async function getOrder(id: string): Promise<Order | null> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return mockOrders.find((o) => o.id === id) || null
  }

  const response = await fetch(`/api/orders/${id}`)
  if (!response.ok) throw new Error("Failed to fetch order")
  return response.json()
}

export async function updateOrderStatus(
  id: string,
  status: Order["order_status"]
): Promise<Order> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const order = mockOrders.find((o) => o.id === id)
    if (!order) throw new Error("Order not found")

    order.order_status = status
    order.updated_at = new Date().toISOString()
    return order
  }

  const response = await fetch(`/api/orders/${id}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  })
  if (!response.ok) throw new Error("Failed to update order status")
  return response.json()
}
