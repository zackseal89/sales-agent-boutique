// Settings service layer with mock data

export interface BusinessSettings {
  id: string
  business_name: string
  business_description: string
  logo_url?: string
  phone_number: string
  email: string
  address: string
  operating_hours: {
    monday: string
    tuesday: string
    wednesday: string
    thursday: string
    friday: string
    saturday: string
    sunday: string
  }
  updated_at: string
}

export interface WhatsAppConfig {
  twilio_account_sid: string
  twilio_auth_token: string
  twilio_phone_number: string
  webhook_url: string
  enabled: boolean
}

export interface PaymentConfig {
  paylink_merchant_id: string
  paylink_api_key: string
  delivery_fee: number
  free_delivery_threshold: number
  enabled: boolean
}

export interface AIAgentConfig {
  greeting_message: string
  tone: "friendly" | "professional" | "casual"
  auto_respond: boolean
  response_delay_seconds: number
}

// Mock data
const mockBusinessSettings: BusinessSettings = {
  id: "business-1",
  business_name: "Fashion Boutique Kenya",
  business_description: "Premium fashion boutique offering the latest trends in women's clothing",
  logo_url: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200",
  phone_number: "+254700000000",
  email: "info@fashionboutique.co.ke",
  address: "Westlands, Nairobi, Kenya",
  operating_hours: {
    monday: "9:00 AM - 6:00 PM",
    tuesday: "9:00 AM - 6:00 PM",
    wednesday: "9:00 AM - 6:00 PM",
    thursday: "9:00 AM - 6:00 PM",
    friday: "9:00 AM - 6:00 PM",
    saturday: "10:00 AM - 4:00 PM",
    sunday: "Closed",
  },
  updated_at: new Date().toISOString(),
}

const mockWhatsAppConfig: WhatsAppConfig = {
  twilio_account_sid: "AC********************************",
  twilio_auth_token: "********************************",
  twilio_phone_number: "+254700000000",
  webhook_url: "https://your-backend.run.app/webhook/whatsapp",
  enabled: true,
}

const mockPaymentConfig: PaymentConfig = {
  paylink_merchant_id: "MERCHANT_ID_HERE",
  paylink_api_key: "********************************",
  delivery_fee: 300,
  free_delivery_threshold: 10000,
  enabled: true,
}

const mockAIAgentConfig: AIAgentConfig = {
  greeting_message: "Hi! 👋 Welcome to Fashion Boutique Kenya. How can I help you today?",
  tone: "friendly",
  auto_respond: true,
  response_delay_seconds: 2,
}

// Toggle between mock and real API
const USE_MOCK_API = true

// Service functions
export async function getBusinessSettings(): Promise<BusinessSettings> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockBusinessSettings
  }

  const response = await fetch("/api/settings/business")
  if (!response.ok) throw new Error("Failed to fetch business settings")
  return response.json()
}

export async function updateBusinessSettings(
  settings: Partial<BusinessSettings>
): Promise<BusinessSettings> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    Object.assign(mockBusinessSettings, settings)
    mockBusinessSettings.updated_at = new Date().toISOString()
    return mockBusinessSettings
  }

  const response = await fetch("/api/settings/business", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  })
  if (!response.ok) throw new Error("Failed to update business settings")
  return response.json()
}

export async function getWhatsAppConfig(): Promise<WhatsAppConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockWhatsAppConfig
  }

  const response = await fetch("/api/settings/whatsapp")
  if (!response.ok) throw new Error("Failed to fetch WhatsApp config")
  return response.json()
}

export async function updateWhatsAppConfig(
  config: Partial<WhatsAppConfig>
): Promise<WhatsAppConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    Object.assign(mockWhatsAppConfig, config)
    return mockWhatsAppConfig
  }

  const response = await fetch("/api/settings/whatsapp", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  })
  if (!response.ok) throw new Error("Failed to update WhatsApp config")
  return response.json()
}

export async function getPaymentConfig(): Promise<PaymentConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockPaymentConfig
  }

  const response = await fetch("/api/settings/payment")
  if (!response.ok) throw new Error("Failed to fetch payment config")
  return response.json()
}

export async function updatePaymentConfig(
  config: Partial<PaymentConfig>
): Promise<PaymentConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    Object.assign(mockPaymentConfig, config)
    return mockPaymentConfig
  }

  const response = await fetch("/api/settings/payment", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  })
  if (!response.ok) throw new Error("Failed to update payment config")
  return response.json()
}

export async function getAIAgentConfig(): Promise<AIAgentConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockAIAgentConfig
  }

  const response = await fetch("/api/settings/ai-agent")
  if (!response.ok) throw new Error("Failed to fetch AI agent config")
  return response.json()
}

export async function updateAIAgentConfig(
  config: Partial<AIAgentConfig>
): Promise<AIAgentConfig> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    Object.assign(mockAIAgentConfig, config)
    return mockAIAgentConfig
  }

  const response = await fetch("/api/settings/ai-agent", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  })
  if (!response.ok) throw new Error("Failed to update AI agent config")
  return response.json()
}
