import { useState, useEffect } from 'react'
import { History, RotateCcw, Eye } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { aiSettingsService, type PromptVersion } from '@/services/ai-settings'
import { formatDistanceToNow } from 'date-fns'

interface VersionHistoryProps {
  boutiqueId: string
  onRollback: () => void
}

export function VersionHistory({ boutiqueId, onRollback }: VersionHistoryProps) {
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null)
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  
  useEffect(() => {
    loadHistory()
  }, [boutiqueId])
  
  const loadHistory = async () => {
    try {
      setLoading(true)
      const data = await aiSettingsService.getHistory(boutiqueId)
      setVersions(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleRollback = async (version: number) => {
    if (!confirm(`Are you sure you want to rollback to version ${version}?`)) {
      return
    }
    
    try {
      await aiSettingsService.rollback(boutiqueId, version)
      onRollback()
    } catch (err) {
      console.error('Failed to rollback:', err)
      alert('Failed to rollback. Please try again.')
    }
  }
  
  const viewVersion = (version: PromptVersion) => {
    setSelectedVersion(version)
    setIsViewDialogOpen(true)
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <History className="h-8 w-8 animate-pulse text-muted-foreground" />
      </div>
    )
  }
  
  if (versions.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No version history yet</p>
          <p className="text-sm">Changes will appear here after you update settings</p>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3">
          {versions.map((version, index) => (
            <Card key={version.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant={index === 0 ? 'default' : 'outline'}>
                        Version {version.version}
                      </Badge>
                      {index === 0 && (
                        <Badge variant="secondary">Current</Badge>
                      )}
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                    </div>
                    
                    <div className="text-sm space-y-1">
                      <div>
                        <span className="font-medium">Tone:</span> {version.tone}
                      </div>
                      <div>
                        <span className="font-medium">Style:</span> {version.language_style}
                      </div>
                      <div>
                        <span className="font-medium">Upsell Rules:</span> {version.upsell_rules.length}
                      </div>
                      <div>
                        <span className="font-medium">Forbidden Phrases:</span> {version.do_not_say.length}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => viewVersion(version)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    {index !== 0 && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRollback(version.version)}
                      >
                        <RotateCcw className="h-4 w-4 mr-1" />
                        Rollback
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
      
      {/* View Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Version {selectedVersion?.version} Details</DialogTitle>
          </DialogHeader>
          
          {selectedVersion && (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">System Prompt</h4>
                <div className="bg-muted p-3 rounded-md text-sm whitespace-pre-wrap">
                  {selectedVersion.system_prompt}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Tone</h4>
                  <Badge>{selectedVersion.tone}</Badge>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Language Style</h4>
                  <Badge>{selectedVersion.language_style}</Badge>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Upsell Rules</h4>
                <div className="space-y-2">
                  {selectedVersion.upsell_rules.map((rule, i) => (
                    <div key={i} className="bg-muted p-2 rounded text-sm">
                      <div><strong>When:</strong> {rule.trigger}</div>
                      <div><strong>Then:</strong> {rule.action}</div>
                      <div><strong>Message:</strong> "{rule.message}"</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Forbidden Phrases</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedVersion.do_not_say.map((phrase, i) => (
                    <Badge key={i} variant="secondary">{phrase}</Badge>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
