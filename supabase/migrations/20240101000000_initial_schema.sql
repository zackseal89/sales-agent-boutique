-- =====================================================
-- Fashion Boutique AI Sales Agent - Complete Database Schema
-- Supabase PostgreSQL with pgvector for semantic search
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =====================================================
-- BOUTIQUES TABLE
-- =====================================================
CREATE TABLE boutiques (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    whatsapp_number VARCHAR(20) UNIQUE NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    owner_email VARCHAR(255) UNIQUE NOT NULL,
    owner_whatsapp VARCHAR(20),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    subscription_plan VARCHAR(50) DEFAULT 'starter',
    is_active BOOLEAN DEFAULT true,
    onboarding_completed BOOLEAN DEFAULT false,
    agent_personality TEXT,
    business_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PRODUCTS TABLE
-- =====================================================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    sizes JSONB DEFAULT '[]'::jsonb,
    colors JSONB DEFAULT '[]'::jsonb,
    stock_quantity INTEGER DEFAULT 0,
    tags JSONB DEFAULT '[]'::jsonb,
    image_urls JSONB DEFAULT '[]'::jsonb,
    embedding vector(768),  -- For semantic search (Gemini embeddings)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX products_embedding_idx ON products USING ivfflat (embedding vector_cosine_ops);

-- =====================================================
-- CUSTOMERS TABLE
-- =====================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    whatsapp_number VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    preferred_size VARCHAR(10),
    size_history JSONB DEFAULT '{}'::jsonb,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    last_order_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(boutique_id, whatsapp_number)
);

-- =====================================================
-- CONVERSATIONS TABLE
-- =====================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    state JSONB DEFAULT '{}'::jsonb,
    current_step VARCHAR(100),
    messages JSONB DEFAULT '[]'::jsonb,
    cart JSONB DEFAULT '[]'::jsonb,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ORDERS TABLE
-- =====================================================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boutique_id UUID NOT NULL REFERENCES boutiques(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    items JSONB NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    delivery_fee DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    delivery_address TEXT,
    payment_status VARCHAR(50) DEFAULT 'pending',
    mpesa_receipt VARCHAR(100),
    checkout_request_id VARCHAR(100),
    order_status VARCHAR(50) DEFAULT 'pending',
    paid_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE boutiques ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Boutiques: Users can only see their own boutique
CREATE POLICY "Users can view own boutique"
    ON boutiques FOR SELECT
    USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own boutique"
    ON boutiques FOR UPDATE
    USING (auth.uid()::text = id::text);

-- Products: Boutiques can only see/manage their own products
CREATE POLICY "Boutiques can view own products"
    ON products FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

CREATE POLICY "Boutiques can insert own products"
    ON products FOR INSERT
    WITH CHECK (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

CREATE POLICY "Boutiques can update own products"
    ON products FOR UPDATE
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

CREATE POLICY "Boutiques can delete own products"
    ON products FOR DELETE
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- Customers: Boutiques can only see their own customers
CREATE POLICY "Boutiques can view own customers"
    ON customers FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- Conversations: Boutiques can only see their own conversations
CREATE POLICY "Boutiques can view own conversations"
    ON conversations FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- Orders: Boutiques can only see their own orders
CREATE POLICY "Boutiques can view own orders"
    ON orders FOR SELECT
    USING (boutique_id IN (
        SELECT id FROM boutiques WHERE auth.uid()::text = id::text
    ));

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_products(
    query_embedding vector(768),
    match_threshold FLOAT,
    match_count INT,
    boutique_id_filter UUID
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    price DECIMAL,
    image_urls JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        id,
        name,
        description,
        price,
        image_urls,
        1 - (embedding <=> query_embedding) AS similarity
    FROM products
    WHERE 
        boutique_id = boutique_id_filter
        AND is_active = true
        AND embedding IS NOT NULL
        AND 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_boutiques_updated_at BEFORE UPDATE ON boutiques
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA FOR TESTING
-- =====================================================

-- Insert test boutique
INSERT INTO boutiques (
    id, name, whatsapp_number, owner_name, owner_email, 
    owner_whatsapp, subscription_status, is_active, onboarding_completed
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Nairobi Fashion House',
    '254712345678',
    'Jane Wanjiku',
    'jane@nairobi-fashion.com',
    '254712345678',
    'active',
    true,
    true
);

-- Insert sample products
INSERT INTO products (boutique_id, name, description, category, price, sizes, colors, stock_quantity, tags, image_urls) VALUES
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Floral Summer Dress',
    'Beautiful flowing dress with vibrant floral patterns. Perfect for casual outings and summer parties. Made from breathable cotton blend.',
    'dresses',
    2500.00,
    '["S", "M", "L", "XL"]'::jsonb,
    '["blue", "pink", "yellow"]'::jsonb,
    15,
    '["summer", "casual", "floral", "trending"]'::jsonb,
    '["https://example.com/dress1.jpg"]'::jsonb
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Elegant Evening Gown',
    'Stunning floor-length gown for special occasions. Features elegant draping and flattering silhouette.',
    'dresses',
    4500.00,
    '["S", "M", "L"]'::jsonb,
    '["red", "black", "navy"]'::jsonb,
    8,
    '["formal", "evening", "party", "wedding"]'::jsonb,
    '["https://example.com/gown1.jpg"]'::jsonb
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Casual Denim Jacket',
    'Classic denim jacket perfect for layering. Versatile and timeless style.',
    'jackets',
    3200.00,
    '["S", "M", "L", "XL"]'::jsonb,
    '["blue", "black"]'::jsonb,
    12,
    '["casual", "denim", "classic"]'::jsonb,
    '["https://example.com/jacket1.jpg"]'::jsonb
);
