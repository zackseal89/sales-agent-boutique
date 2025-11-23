import { useState } from 'react'
import { X, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'

interface ForbiddenPhrasesProps {
  phrases: string[]
  onChange: (phrases: string[]) => void
}

export function ForbiddenPhrases({ phrases, onChange }: ForbiddenPhrasesProps) {
  const [inputValue, setInputValue] = useState('')
  
  const addPhrase = () => {
    const trimmed = inputValue.trim().toLowerCase()
    if (trimmed && !phrases.includes(trimmed)) {
      onChange([...phrases, trimmed])
      setInputValue('')
    }
  }
  
  const removePhrase = (phrase: string) => {
    onChange(phrases.filter(p => p !== phrase))
  }
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addPhrase()
    }
  }
  
  return (
    <div className="space-y-3">
      <Label>Forbidden Phrases</Label>
      
      {/* Tag display */}
      <div className="flex flex-wrap gap-2 min-h-[60px] p-3 border rounded-md bg-muted/30">
        {phrases.length === 0 ? (
          <p className="text-sm text-muted-foreground">No forbidden phrases yet</p>
        ) : (
          phrases.map((phrase) => (
            <Badge key={phrase} variant="secondary" className="gap-1">
              {phrase}
              <button
                onClick={() => removePhrase(phrase)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))
        )}
      </div>
      
      {/* Input */}
      <div className="flex gap-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a phrase and press Enter..."
          className="flex-1"
        />
        <Button onClick={addPhrase} size="icon" variant="outline">
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      
      <p className="text-xs text-muted-foreground">
        Words or phrases the AI should never use in responses
      </p>
    </div>
  )
}
