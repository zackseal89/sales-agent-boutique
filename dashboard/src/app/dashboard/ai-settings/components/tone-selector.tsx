import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'

interface ToneSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function ToneSelector({ value, onChange }: ToneSelectorProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="tone">Tone</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="tone">
          <SelectValue placeholder="Select tone" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="friendly">😊 Friendly</SelectItem>
          <SelectItem value="professional">💼 Professional</SelectItem>
          <SelectItem value="enthusiastic">🎉 Enthusiastic</SelectItem>
          <SelectItem value="casual">😎 Casual</SelectItem>
          <SelectItem value="formal">🎩 Formal</SelectItem>
        </SelectContent>
      </Select>
      <p className="text-xs text-muted-foreground">
        How your agent communicates with customers
      </p>
    </div>
  )
}
