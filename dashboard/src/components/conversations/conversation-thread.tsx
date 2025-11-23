"use client"

import { useState, useEffect } from "react"
import { ConversationDetail, Message, getConversation } from "@/services/conversations"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { CheckCircle2, XCircle, Clock, Image as ImageIcon } from "lucide-react"

interface ConversationThreadProps {
  conversationId: string
}

export function ConversationThread({ conversationId }: ConversationThreadProps) {
  const [conversation, setConversation] = useState<ConversationDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadConversation() {
      setLoading(true)
      try {
        const data = await getConversation(conversationId)
        setConversation(data)
      } catch (error) {
        console.error("Failed to load conversation:", error)
      } finally {
        setLoading(false)
      }
    }

    loadConversation()
  }, [conversationId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-muted-foreground">Loading messages...</p>
      </div>
    )
  }

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-muted-foreground">Conversation not found</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b p-4">
        <h3 className="font-semibold">{conversation.customer_name}</h3>
        <p className="text-sm text-muted-foreground">{conversation.customer_phone}</p>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {conversation.messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </div>
      </ScrollArea>

      {/* Read-only notice */}
      <div className="border-t p-4 bg-muted/50">
        <p className="text-xs text-muted-foreground text-center">
          💬 This is a read-only view. Customers interact via WhatsApp.
        </p>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isCustomer = message.sender === "customer"

  return (
    <div className={cn("flex", isCustomer ? "justify-start" : "justify-end")}>
      <div
        className={cn(
          "max-w-[70%] rounded-lg p-3 space-y-2",
          isCustomer
            ? "bg-muted text-foreground"
            : "bg-primary text-primary-foreground"
        )}
      >
        {/* Image if present */}
        {message.media_url && (
          <div className="relative rounded overflow-hidden">
            <img
              src={message.media_url}
              alt="Message attachment"
              className="w-full h-auto max-h-64 object-cover"
            />
            {message.media_type === "image" && (
              <div className="absolute top-2 right-2">
                <Badge variant="secondary" className="gap-1">
                  <ImageIcon className="h-3 w-3" />
                  Image
                </Badge>
              </div>
            )}
          </div>
        )}

        {/* Message content */}
        {message.content && (
          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        )}

        {/* Payment status */}
        {message.payment_status && (
          <div className="flex items-center gap-2">
            {message.payment_status === "completed" && (
              <Badge variant="default" className="gap-1 bg-green-600">
                <CheckCircle2 className="h-3 w-3" />
                Payment Completed
              </Badge>
            )}
            {message.payment_status === "pending" && (
              <Badge variant="secondary" className="gap-1">
                <Clock className="h-3 w-3" />
                Payment Pending
              </Badge>
            )}
            {message.payment_status === "failed" && (
              <Badge variant="destructive" className="gap-1">
                <XCircle className="h-3 w-3" />
                Payment Failed
              </Badge>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p
          className={cn(
            "text-xs",
            isCustomer ? "text-muted-foreground" : "text-primary-foreground/70"
          )}
        >
          {format(new Date(message.created_at), "h:mm a")}
        </p>
      </div>
    </div>
  )
}
