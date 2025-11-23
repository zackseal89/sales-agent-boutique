"use client"

import { useState, useEffect } from 'react'
import { Bot, Save, History, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { aiSettingsService, type AISettings } from '@/services/ai-settings'
import { PromptEditor } from './components/prompt-editor'
import { ToneSelector } from './components/tone-selector'
import { LanguageStyleSelector } from './components/language-style-selector'
import { UpsellRulesBuilder } from './components/upsell-rules-builder'
import { ForbiddenPhrases } from './components/forbidden-phrases'
import { PreviewPanel } from './components/preview-panel'
import { VersionHistory } from './components/version-history'

export default function AISettingsPage() {
  const [settings, setSettings] = useState<AISettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // TODO: Get actual boutique ID from auth context
  const boutiqueId = '550e8400-e29b-41d4-a716-446655440000'
  
  useEffect(() => {
    loadSettings()
  }, [])
  
  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await aiSettingsService.getSettings(boutiqueId)
      setSettings(data)
      setError(null)
    } catch (err) {
      setError('Failed to load AI settings')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSave = async () => {
    if (!settings) return
    
    try {
      setSaving(true)
      await aiSettingsService.updateSettings(boutiqueId, {
        system_prompt: settings.system_prompt,
        tone: settings.tone,
        language_style: settings.language_style,
        upsell_rules: settings.upsell_rules,
        do_not_say: settings.do_not_say
      })
      setHasChanges(false)
      setError(null)
      // Reload to get new version number
      await loadSettings()
    } catch (err) {
      setError('Failed to save settings')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }
  
  const updateSettings = (updates: Partial<AISettings>) => {
    if (settings) {
      setSettings({ ...settings, ...updates })
      setHasChanges(true)
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Bot className="h-12 w-12 animate-pulse mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading AI settings...</p>
        </div>
      </div>
    )
  }
  
  if (!settings) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error || 'No AI settings found. Please contact support.'}
        </AlertDescription>
      </Alert>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Bot className="h-8 w-8" />
            AI Agent Configuration
          </h1>
          <p className="text-muted-foreground mt-1">
            Customize your AI sales agent's behavior and personality
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-sm">
            Version {settings.prompt_version}
          </Badge>
          <Button 
            onClick={handleSave} 
            disabled={!hasChanges || saving}
            size="lg"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>
      
      {/* Unsaved changes warning */}
      {hasChanges && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            You have unsaved changes. Click "Save Changes" to apply them.
          </AlertDescription>
        </Alert>
      )}
      
      {/* Error message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {/* Main Content */}
      <Tabs defaultValue="settings" className="space-y-6">
        <TabsList>
          <TabsTrigger value="settings">Settings</TabsTrigger>
          <TabsTrigger value="history">
            <History className="h-4 w-4 mr-2" />
            Version History
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Settings */}
            <div className="lg:col-span-2 space-y-6">
              {/* System Prompt */}
              <Card>
                <CardHeader>
                  <CardTitle>System Prompt</CardTitle>
                  <CardDescription>
                    Core instructions that define your AI agent's role and behavior
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <PromptEditor
                    value={settings.system_prompt}
                    onChange={(value) => updateSettings({ system_prompt: value })}
                  />
                </CardContent>
              </Card>
              
              {/* Tone & Style */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Communication Tone</CardTitle>
                    <CardDescription>
                      How your agent speaks to customers
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ToneSelector
                      value={settings.tone}
                      onChange={(value) => updateSettings({ tone: value })}
                    />
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle>Language Style</CardTitle>
                    <CardDescription>
                      Formality level of communication
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <LanguageStyleSelector
                      value={settings.language_style}
                      onChange={(value) => updateSettings({ language_style: value })}
                    />
                  </CardContent>
                </Card>
              </div>
              
              {/* Upsell Rules */}
              <Card>
                <CardHeader>
                  <CardTitle>Upsell Rules</CardTitle>
                  <CardDescription>
                    Define when and how to suggest additional products
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <UpsellRulesBuilder
                    rules={settings.upsell_rules}
                    onChange={(rules) => updateSettings({ upsell_rules: rules })}
                  />
                </CardContent>
              </Card>
              
              {/* Forbidden Phrases */}
              <Card>
                <CardHeader>
                  <CardTitle>Forbidden Phrases</CardTitle>
                  <CardDescription>
                    Words or phrases the AI should never use
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ForbiddenPhrases
                    phrases={settings.do_not_say}
                    onChange={(phrases) => updateSettings({ do_not_say: phrases })}
                  />
                </CardContent>
              </Card>
            </div>
            
            {/* Right Column - Preview */}
            <div className="lg:col-span-1">
              <div className="sticky top-6">
                <PreviewPanel settings={settings} />
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="history">
          <VersionHistory 
            boutiqueId={boutiqueId}
            onRollback={loadSettings}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
