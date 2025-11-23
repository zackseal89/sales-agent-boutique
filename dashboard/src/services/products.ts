// Mock product data and service layer
// This allows frontend development without backend dependency

export interface Product {
  id: string
  name: string
  price: number
  description: string
  image_url: string
  stock_quantity: number
  category: string
  // Fashion-specific fields
  size?: string[]
  color?: string[]
  style?: string
  season?: string
  instagram_reference?: string
  created_at?: string
  updated_at?: string
}

// Mock data
const mockProducts: Product[] = [
  {
    id: "1",
    name: "Floral Summer Dress",
    price: 4500,
    description: "Light and breezy floral dress perfect for summer occasions",
    image_url: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
    stock_quantity: 15,
    category: "Dresses",
    size: ["S", "M", "L", "XL"],
    color: ["Blue", "Pink", "White"],
    style: "Casual",
    season: "Summer",
    instagram_reference: "@fashionboutique/post123",
  },
  {
    id: "2",
    name: "Classic Denim Jacket",
    price: 6800,
    description: "Timeless denim jacket that goes with everything",
    image_url: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
    stock_quantity: 8,
    category: "Jackets",
    size: ["S", "M", "L"],
    color: ["Blue", "Black"],
    style: "Casual",
    season: "All Season",
  },
  {
    id: "3",
    name: "Elegant Evening Gown",
    price: 12500,
    description: "Stunning evening gown for special occasions",
    image_url: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400",
    stock_quantity: 5,
    category: "Dresses",
    size: ["S", "M", "L"],
    color: ["Black", "Red", "Navy"],
    style: "Formal",
    season: "All Season",
  },
]

// Toggle between mock and real API
const USE_MOCK_API = true

// Service functions
export async function getProducts(): Promise<Product[]> {
  if (USE_MOCK_API) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockProducts
  }
  
  // Real API call (to be implemented)
  const response = await fetch("/api/products")
  if (!response.ok) throw new Error("Failed to fetch products")
  return response.json()
}

export async function getProduct(id: string): Promise<Product | null> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return mockProducts.find((p) => p.id === id) || null
  }
  
  const response = await fetch(`/api/products/${id}`)
  if (!response.ok) throw new Error("Failed to fetch product")
  return response.json()
}

export async function createProduct(product: Omit<Product, "id">): Promise<Product> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const newProduct = {
      ...product,
      id: Math.random().toString(36).substr(2, 9),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    mockProducts.push(newProduct)
    return newProduct
  }
  
  const response = await fetch("/api/products", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(product),
  })
  if (!response.ok) throw new Error("Failed to create product")
  return response.json()
}

export async function updateProduct(id: string, product: Partial<Product>): Promise<Product> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const index = mockProducts.findIndex((p) => p.id === id)
    if (index === -1) throw new Error("Product not found")
    
    mockProducts[index] = {
      ...mockProducts[index],
      ...product,
      updated_at: new Date().toISOString(),
    }
    return mockProducts[index]
  }
  
  const response = await fetch(`/api/products/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(product),
  })
  if (!response.ok) throw new Error("Failed to update product")
  return response.json()
}

export async function deleteProduct(id: string): Promise<void> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const index = mockProducts.findIndex((p) => p.id === id)
    if (index === -1) throw new Error("Product not found")
    mockProducts.splice(index, 1)
    return
  }
  
  const response = await fetch(`/api/products/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error("Failed to delete product")
}
