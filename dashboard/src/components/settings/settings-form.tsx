"use client"

import { useState, useEffect } from "react"
import {
  BusinessSettings,
  WhatsAppConfig,
  PaymentConfig,
  AIAgentConfig,
  getBusinessSettings,
  getWhatsAppConfig,
  getPaymentConfig,
  getAIAgentConfig,
  updateBusinessSettings,
  updateWhatsAppConfig,
  updatePaymentConfig,
  updateAIAgentConfig,
} from "@/services/settings"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"
import { Building2, MessageSquare, CreditCard, Bot } from "lucide-react"

export function SettingsForm() {
  // const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Business settings
  const [businessSettings, setBusinessSettings] = useState<BusinessSettings | null>(null)
  const [whatsappConfig, setWhatsappConfig] = useState<WhatsAppConfig | null>(null)
  const [paymentConfig, setPaymentConfig] = useState<PaymentConfig | null>(null)
  const [aiAgentConfig, setAIAgentConfig] = useState<AIAgentConfig | null>(null)

  useEffect(() => {
    async function loadSettings() {
      try {
        const [business, whatsapp, payment, aiAgent] = await Promise.all([
          getBusinessSettings(),
          getWhatsAppConfig(),
          getPaymentConfig(),
          getAIAgentConfig(),
        ])
        setBusinessSettings(business)
        setWhatsappConfig(whatsapp)
        setPaymentConfig(payment)
        setAIAgentConfig(aiAgent)
      } catch (error) {
        console.error("Failed to load settings:", error)
        console.error("Failed to load settings:", error)
        toast.error("Error", {
          description: "Failed to load settings",
        })
      } finally {
        setLoading(false)
      }
    }

    loadSettings()
  }, [])

  async function handleSaveBusinessSettings() {
    if (!businessSettings) return

    setSaving(true)
    try {
      await updateBusinessSettings(businessSettings)
      await updateBusinessSettings(businessSettings)
      toast.success("Success", {
        description: "Business settings updated successfully",
      })
    } catch (error) {
      console.error("Failed to update business settings:", error)
      console.error("Failed to update business settings:", error)
      toast.error("Error", {
        description: "Failed to update business settings",
      })
    } finally {
      setSaving(false)
    }
  }

  async function handleSaveWhatsAppConfig() {
    if (!whatsappConfig) return

    setSaving(true)
    try {
      await updateWhatsAppConfig(whatsappConfig)
      await updateWhatsAppConfig(whatsappConfig)
      toast.success("Success", {
        description: "WhatsApp settings updated successfully",
      })
    } catch (error) {
      console.error("Failed to update WhatsApp settings:", error)
      console.error("Failed to update WhatsApp settings:", error)
      toast.error("Error", {
        description: "Failed to update WhatsApp settings",
      })
    } finally {
      setSaving(false)
    }
  }

  async function handleSavePaymentConfig() {
    if (!paymentConfig) return

    setSaving(true)
    try {
      await updatePaymentConfig(paymentConfig)
      await updatePaymentConfig(paymentConfig)
      toast.success("Success", {
        description: "Payment settings updated successfully",
      })
    } catch (error) {
      console.error("Failed to update payment settings:", error)
      console.error("Failed to update payment settings:", error)
      toast.error("Error", {
        description: "Failed to update payment settings",
      })
    } finally {
      setSaving(false)
    }
  }

  async function handleSaveAIAgentConfig() {
    if (!aiAgentConfig) return

    setSaving(true)
    try {
      await updateAIAgentConfig(aiAgentConfig)
      await updateAIAgentConfig(aiAgentConfig)
      toast.success("Success", {
        description: "AI Agent settings updated successfully",
      })
    } catch (error) {
      console.error("Failed to update AI Agent settings:", error)
      console.error("Failed to update AI Agent settings:", error)
      toast.error("Error", {
        description: "Failed to update AI Agent settings",
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Loading settings...</p>
      </div>
    )
  }

  return (
    <Tabs defaultValue="business" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="business">
          <Building2 className="h-4 w-4 mr-2" />
          Business
        </TabsTrigger>
        <TabsTrigger value="whatsapp">
          <MessageSquare className="h-4 w-4 mr-2" />
          WhatsApp
        </TabsTrigger>
        <TabsTrigger value="payment">
          <CreditCard className="h-4 w-4 mr-2" />
          Payment
        </TabsTrigger>
        <TabsTrigger value="ai-agent">
          <Bot className="h-4 w-4 mr-2" />
          AI Agent
        </TabsTrigger>
      </TabsList>

      {/* Business Settings */}
      <TabsContent value="business">
        <Card>
          <CardHeader>
            <CardTitle>Business Profile</CardTitle>
            <CardDescription>
              Manage your business information and operating hours
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {businessSettings && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="business-name">Business Name</Label>
                  <Input
                    id="business-name"
                    value={businessSettings.business_name}
                    onChange={(e) =>
                      setBusinessSettings({
                        ...businessSettings,
                        business_name: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="business-description">Description</Label>
                  <Textarea
                    id="business-description"
                    value={businessSettings.business_description}
                    onChange={(e) =>
                      setBusinessSettings({
                        ...businessSettings,
                        business_description: e.target.value,
                      })
                    }
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={businessSettings.phone_number}
                      onChange={(e) =>
                        setBusinessSettings({
                          ...businessSettings,
                          phone_number: e.target.value,
                        })
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={businessSettings.email}
                      onChange={(e) =>
                        setBusinessSettings({
                          ...businessSettings,
                          email: e.target.value,
                        })
                      }
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={businessSettings.address}
                    onChange={(e) =>
                      setBusinessSettings({
                        ...businessSettings,
                        address: e.target.value,
                      })
                    }
                  />
                </div>

                <Button onClick={handleSaveBusinessSettings} disabled={saving}>
                  {saving ? "Saving..." : "Save Business Settings"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* WhatsApp Settings */}
      <TabsContent value="whatsapp">
        <Card>
          <CardHeader>
            <CardTitle>WhatsApp Configuration</CardTitle>
            <CardDescription>
              Configure your Twilio WhatsApp Business API integration
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {whatsappConfig && (
              <>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>WhatsApp Integration</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable or disable WhatsApp messaging
                    </p>
                  </div>
                  <Switch
                    checked={whatsappConfig.enabled}
                    onCheckedChange={(checked) =>
                      setWhatsappConfig({ ...whatsappConfig, enabled: checked })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="twilio-sid">Twilio Account SID</Label>
                  <Input
                    id="twilio-sid"
                    type="password"
                    value={whatsappConfig.twilio_account_sid}
                    onChange={(e) =>
                      setWhatsappConfig({
                        ...whatsappConfig,
                        twilio_account_sid: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="twilio-token">Twilio Auth Token</Label>
                  <Input
                    id="twilio-token"
                    type="password"
                    value={whatsappConfig.twilio_auth_token}
                    onChange={(e) =>
                      setWhatsappConfig({
                        ...whatsappConfig,
                        twilio_auth_token: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="twilio-phone">Twilio Phone Number</Label>
                  <Input
                    id="twilio-phone"
                    value={whatsappConfig.twilio_phone_number}
                    onChange={(e) =>
                      setWhatsappConfig({
                        ...whatsappConfig,
                        twilio_phone_number: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="webhook-url">Webhook URL</Label>
                  <Input
                    id="webhook-url"
                    value={whatsappConfig.webhook_url}
                    onChange={(e) =>
                      setWhatsappConfig({
                        ...whatsappConfig,
                        webhook_url: e.target.value,
                      })
                    }
                  />
                  <p className="text-xs text-muted-foreground">
                    Configure this URL in your Twilio console
                  </p>
                </div>

                <Button onClick={handleSaveWhatsAppConfig} disabled={saving}>
                  {saving ? "Saving..." : "Save WhatsApp Settings"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* Payment Settings */}
      <TabsContent value="payment">
        <Card>
          <CardHeader>
            <CardTitle>Payment Configuration</CardTitle>
            <CardDescription>
              Configure M-Pesa payment integration via PayLink
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {paymentConfig && (
              <>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>M-Pesa Payments</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable or disable M-Pesa payment processing
                    </p>
                  </div>
                  <Switch
                    checked={paymentConfig.enabled}
                    onCheckedChange={(checked) =>
                      setPaymentConfig({ ...paymentConfig, enabled: checked })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="merchant-id">PayLink Merchant ID</Label>
                  <Input
                    id="merchant-id"
                    value={paymentConfig.paylink_merchant_id}
                    onChange={(e) =>
                      setPaymentConfig({
                        ...paymentConfig,
                        paylink_merchant_id: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="api-key">PayLink API Key</Label>
                  <Input
                    id="api-key"
                    type="password"
                    value={paymentConfig.paylink_api_key}
                    onChange={(e) =>
                      setPaymentConfig({
                        ...paymentConfig,
                        paylink_api_key: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="delivery-fee">Delivery Fee (KES)</Label>
                    <Input
                      id="delivery-fee"
                      type="number"
                      value={paymentConfig.delivery_fee}
                      onChange={(e) =>
                        setPaymentConfig({
                          ...paymentConfig,
                          delivery_fee: Number(e.target.value),
                        })
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="free-delivery">Free Delivery Threshold (KES)</Label>
                    <Input
                      id="free-delivery"
                      type="number"
                      value={paymentConfig.free_delivery_threshold}
                      onChange={(e) =>
                        setPaymentConfig({
                          ...paymentConfig,
                          free_delivery_threshold: Number(e.target.value),
                        })
                      }
                    />
                  </div>
                </div>

                <Button onClick={handleSavePaymentConfig} disabled={saving}>
                  {saving ? "Saving..." : "Save Payment Settings"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* AI Agent Settings */}
      <TabsContent value="ai-agent">
        <Card>
          <CardHeader>
            <CardTitle>AI Agent Behavior</CardTitle>
            <CardDescription>
              Customize how your AI sales agent interacts with customers
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiAgentConfig && (
              <>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Auto-Respond</Label>
                    <p className="text-sm text-muted-foreground">
                      Automatically respond to customer messages
                    </p>
                  </div>
                  <Switch
                    checked={aiAgentConfig.auto_respond}
                    onCheckedChange={(checked) =>
                      setAIAgentConfig({ ...aiAgentConfig, auto_respond: checked })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="greeting">Greeting Message</Label>
                  <Textarea
                    id="greeting"
                    value={aiAgentConfig.greeting_message}
                    onChange={(e) =>
                      setAIAgentConfig({
                        ...aiAgentConfig,
                        greeting_message: e.target.value,
                      })
                    }
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tone">Conversation Tone</Label>
                  <Select
                    value={aiAgentConfig.tone}
                    onValueChange={(value: AIAgentConfig["tone"]) =>
                      setAIAgentConfig({ ...aiAgentConfig, tone: value })
                    }
                  >
                    <SelectTrigger id="tone">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="response-delay">Response Delay (seconds)</Label>
                  <Input
                    id="response-delay"
                    type="number"
                    min="0"
                    max="10"
                    value={aiAgentConfig.response_delay_seconds}
                    onChange={(e) =>
                      setAIAgentConfig({
                        ...aiAgentConfig,
                        response_delay_seconds: Number(e.target.value),
                      })
                    }
                  />
                  <p className="text-xs text-muted-foreground">
                    Add a delay to make responses feel more natural
                  </p>
                </div>

                <Button onClick={handleSaveAIAgentConfig} disabled={saving}>
                  {saving ? "Saving..." : "Save AI Agent Settings"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  )
}
