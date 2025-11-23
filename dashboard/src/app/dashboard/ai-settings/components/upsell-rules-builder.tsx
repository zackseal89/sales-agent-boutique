import { useState } from 'react'
import { Plus, Trash2, Edit } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import type { UpsellRule } from '@/services/ai-settings'

interface UpsellRulesBuilderProps {
  rules: UpsellRule[]
  onChange: (rules: UpsellRule[]) => void
}

export function UpsellRulesBuilder({ rules, onChange }: UpsellRulesBuilderProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [formData, setFormData] = useState<UpsellRule>({
    trigger: '',
    action: '',
    message: ''
  })
  
  const openDialog = (index?: number) => {
    if (index !== undefined) {
      setEditingIndex(index)
      setFormData(rules[index])
    } else {
      setEditingIndex(null)
      setFormData({ trigger: '', action: '', message: '' })
    }
    setIsDialogOpen(true)
  }
  
  const closeDialog = () => {
    setIsDialogOpen(false)
    setEditingIndex(null)
    setFormData({ trigger: '', action: '', message: '' })
  }
  
  const saveRule = () => {
    if (!formData.trigger || !formData.action || !formData.message) return
    
    if (editingIndex !== null) {
      const updated = [...rules]
      updated[editingIndex] = formData
      onChange(updated)
    } else {
      onChange([...rules, formData])
    }
    closeDialog()
  }
  
  const deleteRule = (index: number) => {
    onChange(rules.filter((_, i) => i !== index))
  }
  
  return (
    <div className="space-y-3">
      {/* Rules List */}
      {rules.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No upsell rules configured</p>
          <p className="text-sm">Add rules to suggest products at the right time</p>
        </div>
      ) : (
        <div className="space-y-2">
          {rules.map((rule, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium">When:</span>
                    <code className="bg-muted px-2 py-0.5 rounded text-xs">{rule.trigger}</code>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium">Then:</span>
                    <span className="text-muted-foreground">{rule.action}</span>
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Message:</span> "{rule.message}"
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => openDialog(index)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => deleteRule(index)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
      
      {/* Add Button */}
      <Button onClick={() => openDialog()} variant="outline" className="w-full">
        <Plus className="h-4 w-4 mr-2" />
        Add Upsell Rule
      </Button>
      
      {/* Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingIndex !== null ? 'Edit Upsell Rule' : 'Add Upsell Rule'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="trigger">Trigger Condition</Label>
              <Input
                id="trigger"
                value={formData.trigger}
                onChange={(e) => setFormData({ ...formData, trigger: e.target.value })}
                placeholder="e.g., cart_value > 5000"
              />
              <p className="text-xs text-muted-foreground">
                When should this rule activate?
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="action">Action</Label>
              <Input
                id="action"
                value={formData.action}
                onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                placeholder="e.g., suggest_complementary_items"
              />
              <p className="text-xs text-muted-foreground">
                What should the AI do?
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="message">Message</Label>
              <Input
                id="message"
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                placeholder="e.g., These items would go great together! 👗✨"
              />
              <p className="text-xs text-muted-foreground">
                What should the AI say?
              </p>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>Cancel</Button>
            <Button onClick={saveRule}>
              {editingIndex !== null ? 'Update' : 'Add'} Rule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
