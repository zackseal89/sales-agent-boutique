"use client"

import { useState, useEffect } from "react"
import { Conversation, getConversations } from "@/services/conversations"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { formatDistanceToNow } from "date-fns"
import { cn } from "@/lib/utils"

interface ConversationListProps {
  selectedId?: string
  onSelect: (conversation: Conversation) => void
}

export function ConversationList({ selectedId, onSelect }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadConversations() {
      try {
        const data = await getConversations()
        setConversations(data)
      } catch (error) {
        console.error("Failed to load conversations:", error)
      } finally {
        setLoading(false)
      }
    }

    loadConversations()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-muted-foreground">Loading conversations...</p>
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-muted-foreground">No conversations yet</p>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-1 p-2">
        {conversations.map((conversation) => {
          const initials = conversation.customer_name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .toUpperCase()

          return (
            <button
              key={conversation.id}
              onClick={() => onSelect(conversation)}
              className={cn(
                "w-full text-left p-3 rounded-lg hover:bg-accent transition-colors",
                selectedId === conversation.id && "bg-accent"
              )}
            >
              <div className="flex items-start gap-3">
                <Avatar className="h-10 w-10">
                  <AvatarFallback>{initials}</AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <p className="font-medium text-sm truncate">
                      {conversation.customer_name}
                    </p>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatDistanceToNow(new Date(conversation.last_message_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-1 truncate">
                    {conversation.customer_phone}
                  </p>
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm text-muted-foreground truncate flex-1">
                      {conversation.last_message}
                    </p>
                    {conversation.unread_count > 0 && (
                      <Badge variant="default" className="h-5 min-w-5 px-1.5 text-xs">
                        {conversation.unread_count}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </ScrollArea>
  )
}
