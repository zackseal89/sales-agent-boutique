import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface PromptEditorProps {
  value: string
  onChange: (value: string) => void
  maxLength?: number
}

export function PromptEditor({ value, onChange, maxLength = 5000 }: PromptEditorProps) {
  const charCount = value.length
  const isNearLimit = charCount > maxLength * 0.9
  
  return (
    <div className="space-y-2">
      <Label htmlFor="system-prompt">System Prompt</Label>
      <Textarea
        id="system-prompt"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter your AI agent's system prompt..."
        className="min-h-[300px] font-mono text-sm"
        maxLength={maxLength}
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Define your AI agent's role, personality, and guidelines</span>
        <span className={isNearLimit ? 'text-orange-500' : ''}>
          {charCount} / {maxLength} characters
        </span>
      </div>
    </div>
  )
}
