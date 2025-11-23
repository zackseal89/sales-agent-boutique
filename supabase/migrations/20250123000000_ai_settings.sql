-- =====================================================
-- AI Settings Migration
-- Add boutique_ai_settings table and prompt version tracking
-- =====================================================

-- =====================================================
-- BOUTIQUE_AI_SETTINGS TABLE
-- =====================================================
CREATE TABLE boutique_ai_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    system_prompt TEXT NOT NULL DEFAULT 'You are a helpful fashion sales assistant for a boutique in Kenya. Help customers find products, answer questions, and complete purchases through WhatsApp.',
    tone VARCHAR(50) DEFAULT 'friendly',
    language_style VARCHAR(50) DEFAULT 'conversational',
    upsell_rules JSONB DEFAULT '[]'::jsonb,
    do_not_say TEXT[] DEFAULT ARRAY[]::TEXT[],
    prompt_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(boutique_id)
);

-- Add RLS policy for boutique_ai_settings
ALTER TABLE boutique_ai_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Boutiques can view own AI settings"
    ON boutique_ai_settings FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

CREATE POLICY "Boutiques can update own AI settings"
    ON boutique_ai_settings FOR UPDATE
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

CREATE POLICY "Boutiques can insert own AI settings"
    ON boutique_ai_settings FOR INSERT
    WITH CHECK (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- Create trigger for updated_at
CREATE TRIGGER update_boutique_ai_settings_updated_at 
    BEFORE UPDATE ON boutique_ai_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UPDATE CONVERSATIONS TABLE
-- =====================================================
-- Add prompt_version column to track which AI settings version was used
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS prompt_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_boutique_customer 
    ON conversations(boutique_id, customer_phone);

CREATE INDEX IF NOT EXISTS idx_conversations_status 
    ON conversations(boutique_id, status);

-- =====================================================
-- MESSAGES TABLE (for conversation history)
-- =====================================================
-- Create dedicated messages table (separate from JSONB in conversations)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'agent', 'system')),
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_conversation 
    ON messages(conversation_id, created_at DESC);

-- Add RLS policy for messages
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Boutiques can view own messages"
    ON messages FOR SELECT
    USING (conversation_id IN (
        SELECT id FROM conversations WHERE boutique_id IN (
            SELECT id FROM boutiques WHERE auth.uid()::text = id::text
        )
    ));

-- =====================================================
-- PROMPT_VERSION_HISTORY TABLE
-- =====================================================
-- Track history of AI settings changes for rollback
CREATE TABLE prompt_version_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    system_prompt TEXT NOT NULL,
    tone VARCHAR(50),
    language_style VARCHAR(50),
    upsell_rules JSONB,
    do_not_say TEXT[],
    changed_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for version lookups
CREATE INDEX IF NOT EXISTS idx_prompt_history_boutique_version 
    ON prompt_version_history(boutique_id, version DESC);

-- Add RLS policy
ALTER TABLE prompt_version_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Boutiques can view own prompt history"
    ON prompt_version_history FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- =====================================================
-- FUNCTION: Auto-increment prompt version
-- =====================================================
CREATE OR REPLACE FUNCTION increment_prompt_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Save old version to history
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO prompt_version_history (
            boutique_id, version, system_prompt, tone, 
            language_style, upsell_rules, do_not_say
        ) VALUES (
            OLD.boutique_id, OLD.prompt_version, OLD.system_prompt, 
            OLD.tone, OLD.language_style, OLD.upsell_rules, OLD.do_not_say
        );
        
        -- Increment version
        NEW.prompt_version = OLD.prompt_version + 1;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER auto_increment_prompt_version
    BEFORE UPDATE ON boutique_ai_settings
    FOR EACH ROW
    WHEN (
        OLD.system_prompt IS DISTINCT FROM NEW.system_prompt OR
        OLD.tone IS DISTINCT FROM NEW.tone OR
        OLD.language_style IS DISTINCT FROM NEW.language_style OR
        OLD.upsell_rules IS DISTINCT FROM NEW.upsell_rules OR
        OLD.do_not_say IS DISTINCT FROM NEW.do_not_say
    )
    EXECUTE FUNCTION increment_prompt_version();

-- =====================================================
-- SEED DEFAULT AI SETTINGS
-- =====================================================
-- Insert default AI settings for existing boutique
INSERT INTO boutique_ai_settings (boutique_id, system_prompt, tone, language_style, upsell_rules, do_not_say)
SELECT 
    id,
    'You are a helpful and friendly fashion sales assistant for ' || name || ', a boutique in Kenya. 

Your role is to:
- Help customers discover products through natural conversation
- Provide personalized recommendations based on their preferences
- Answer questions about products, sizes, colors, and availability
- Assist with adding items to cart and completing purchases via M-Pesa
- Track orders and provide delivery updates

Communication style:
- Be warm, professional, and enthusiastic about fashion
- Use simple, clear language
- Respond quickly and concisely (WhatsApp messages should be brief)
- Use emojis sparingly to add personality
- Always confirm customer requests before taking action

When helping customers:
- Ask clarifying questions if their request is unclear
- Suggest similar alternatives if exact items aren''t available
- Mention product features that match their needs
- Provide accurate pricing in KES (Kenyan Shillings)
- Confirm sizes and colors before adding to cart

For payments:
- Clearly explain the M-Pesa payment process
- Confirm the total amount before initiating payment
- Provide order confirmation with tracking details

Remember: You represent ' || name || ' - maintain a professional yet friendly tone that reflects the boutique''s brand.',
    'friendly',
    'conversational',
    '[
        {
            "trigger": "cart_value > 5000",
            "action": "suggest_complementary_items",
            "message": "These items would go great together! 👗✨"
        },
        {
            "trigger": "viewing_dress",
            "action": "suggest_accessories",
            "message": "Would you like to see matching accessories?"
        }
    ]'::jsonb,
    ARRAY['cheap', 'fake', 'knockoff', 'low quality']
FROM boutiques
WHERE id = '550e8400-e29b-41d4-a716-446655440000'
ON CONFLICT (boutique_id) DO NOTHING;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment to verify after migration:
-- SELECT * FROM boutique_ai_settings;
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%ai%';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'conversations';
