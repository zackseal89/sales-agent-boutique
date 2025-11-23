import { supabase } from '@/lib/supabase'

export interface UpsellRule {
  trigger: string
  action: string
  message: string
}

export interface AISettings {
  id: string
  boutique_id: string
  system_prompt: string
  tone: string
  language_style: string
  upsell_rules: UpsellRule[]
  do_not_say: string[]
  prompt_version: number
  created_at: string
  updated_at: string
}

export interface PromptVersion {
  id: string
  boutique_id: string
  version: number
  system_prompt: string
  tone: string
  language_style: string
  upsell_rules: UpsellRule[]
  do_not_say: string[]
  created_at: string
}

export const aiSettingsService = {
  async getSettings(boutiqueId: string): Promise<AISettings> {
    const { data, error } = await supabase
      .from('boutique_ai_settings')
      .select('*')
      .eq('boutique_id', boutiqueId)
      .single()
    
    if (error) throw error
    return data
  },
  
  async updateSettings(boutiqueId: string, settings: Partial<AISettings>): Promise<AISettings> {
    const { data, error } = await supabase
      .from('boutique_ai_settings')
      .update(settings)
      .eq('boutique_id', boutiqueId)
      .select()
      .single()
    
    if (error) throw error
    return data
  },
  
  async getHistory(boutiqueId: string, limit: number = 10): Promise<PromptVersion[]> {
    const { data, error } = await supabase
      .from('prompt_version_history')
      .select('*')
      .eq('boutique_id', boutiqueId)
      .order('version', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data || []
  },
  
  async rollback(boutiqueId: string, version: number): Promise<AISettings> {
    // Get historical version
    const { data: historical, error: histError } = await supabase
      .from('prompt_version_history')
      .select('*')
      .eq('boutique_id', boutiqueId)
      .eq('version', version)
      .single()
    
    if (histError) throw histError
    
    // Update current settings with historical data
    const { data, error } = await supabase
      .from('boutique_ai_settings')
      .update({
        system_prompt: historical.system_prompt,
        tone: historical.tone,
        language_style: historical.language_style,
        upsell_rules: historical.upsell_rules,
        do_not_say: historical.do_not_say
      })
      .eq('boutique_id', boutiqueId)
      .select()
      .single()
    
    if (error) throw error
    return data
  }
}
