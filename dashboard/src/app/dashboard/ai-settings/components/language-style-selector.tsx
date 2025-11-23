import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'

interface LanguageStyleSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function LanguageStyleSelector({ value, onChange }: LanguageStyleSelectorProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="language-style">Language Style</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="language-style">
          <SelectValue placeholder="Select style" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="conversational">💬 Conversational</SelectItem>
          <SelectItem value="formal">📝 Formal</SelectItem>
          <SelectItem value="casual">🗣️ Casual</SelectItem>
        </SelectContent>
      </Select>
      <p className="text-xs text-muted-foreground">
        Formality level of communication
      </p>
    </div>
  )
}
