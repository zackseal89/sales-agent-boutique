"use client"

import { useState } from "react"
import { Conversation } from "@/services/conversations"
import { ConversationList } from "@/components/conversations/conversation-list"
import { ConversationThread } from "@/components/conversations/conversation-thread"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ConversationsPage() {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <Card className="flex-1 flex flex-col min-h-0">
        <CardHeader>
          <CardTitle>Conversations</CardTitle>
          <CardDescription>
            View customer conversations with your AI sales agent. This is a read-only view.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex gap-4 min-h-0">
          {/* Left: Conversation List */}
          <div className="w-80 border-r pr-4">
            <ConversationList
              selectedId={selectedConversation?.id}
              onSelect={setSelectedConversation}
            />
          </div>

          {/* Right: Conversation Thread */}
          <div className="flex-1 min-w-0">
            {selectedConversation ? (
              <ConversationThread conversationId={selectedConversation.id} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-muted-foreground">
                  Select a conversation to view messages
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
