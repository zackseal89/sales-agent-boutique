import { useState } from 'react'
import { Bot, User, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { AISettings } from '@/services/ai-settings'

interface PreviewPanelProps {
  settings: AISettings
}

interface Message {
  role: 'customer' | 'agent'
  content: string
}

export function PreviewPanel({ settings }: PreviewPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'customer', content: 'Do you have red dresses?' }
  ])
  const [input, setInput] = useState('')
  
  const sampleResponses: Record<string, string> = {
    'red dresses': `Yes! We have several beautiful red dresses in stock. Let me show you our top picks:\n\n1. Elegant Red Evening Gown - KES 8,500\n2. Casual Red Sundress - KES 3,200\n3. Red Cocktail Dress - KES 5,800\n\nWhich style interests you? 👗`,
    'price': `Our prices range from KES 2,000 to KES 15,000 depending on the item. What type of product are you interested in?`,
    'buy': `Great! I'd be happy to help you complete your purchase. Let me add that to your cart and we can proceed with M-Pesa payment. 🛍️`,
    'discount': `We occasionally have special promotions! Right now, if you purchase items over KES 5,000, you get free delivery. Would you like to see our current collection?`
  }
  
  const generateResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase()
    
    // Find matching response
    for (const [key, response] of Object.entries(sampleResponses)) {
      if (lowerMessage.includes(key)) {
        return applySettings(response)
      }
    }
    
    return applySettings("I'd be happy to help you with that! Could you tell me more about what you're looking for?")
  }
  
  const applySettings = (baseResponse: string): string => {
    let response = baseResponse
    
    // Apply tone modifications
    if (settings.tone === 'professional') {
      response = response.replace(/!/g, '.')
      response = response.replace(/👗|🛍️|✨/g, '')
    } else if (settings.tone === 'enthusiastic') {
      response = response + ' ✨'
    }
    
    // Check forbidden phrases
    settings.do_not_say.forEach(phrase => {
      const regex = new RegExp(phrase, 'gi')
      response = response.replace(regex, '[filtered]')
    })
    
    return response
  }
  
  const sendMessage = () => {
    if (!input.trim()) return
    
    const userMessage: Message = { role: 'customer', content: input }
    const agentResponse: Message = { 
      role: 'agent', 
      content: generateResponse(input) 
    }
    
    setMessages([...messages, userMessage, agentResponse])
    setInput('')
  }
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      sendMessage()
    }
  }
  
  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="text-lg">Live Preview</CardTitle>
        <p className="text-sm text-muted-foreground">
          Test how your AI agent responds
        </p>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <ScrollArea className="flex-1 px-4">
          <div className="space-y-4 pb-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-2 ${
                  message.role === 'customer' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'agent' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary-foreground" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                    message.role === 'customer'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  {message.content}
                </div>
                {message.role === 'customer' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
        
        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              className="flex-1"
            />
            <Button onClick={sendMessage} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Tone: {settings.tone} | Style: {settings.language_style}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
