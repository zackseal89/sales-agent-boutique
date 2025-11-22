-- Create boutique_info table for general store knowledge
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS boutique_info (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    boutique_id TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'hours', 'location', 'policy', 'about'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_boutique_info_boutique_id ON boutique_info(boutique_id);

-- Add RLS policies (optional but recommended)
ALTER TABLE boutique_info ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON boutique_info
    FOR SELECT USING (true);

-- Seed some sample data for the test boutique
INSERT INTO boutique_info (boutique_id, category, content) VALUES
('b1', 'hours', 'We are open Monday to Saturday from 9:00 AM to 6:00 PM. We are closed on Sundays.'),
('b1', 'location', 'We are located at 123 Fashion Street, Westlands, Nairobi.'),
('b1', 'return_policy', 'We accept returns within 7 days of purchase if the item is unworn and has original tags.'),
('b1', 'contact', 'You can reach us at +254 700 000 000 or email support@fashionboutique.co.ke');
