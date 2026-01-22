-- Eshop Pulse Database Schema (Simplified)
-- Stores only: game images + price history for future charts
-- Game metadata (title, slug, etc.) comes from Git/JSON

-- Game images table - stores cover images by slug
CREATE TABLE IF NOT EXISTS game_images (
    slug VARCHAR(500) PRIMARY KEY,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_game_images_slug ON game_images(slug);

-- Price history table - stores daily price snapshots for charts
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(500) NOT NULL,
    region_code VARCHAR(5) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    msrp DECIMAL(10, 2),
    sale_price DECIMAL(10, 2),
    price_brl DECIMAL(10, 2),
    discount_percent INTEGER DEFAULT 0,
    on_sale BOOLEAN DEFAULT FALSE,
    recorded_at DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(slug, region_code, recorded_at)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_price_history_slug ON price_history(slug);
CREATE INDEX IF NOT EXISTS idx_price_history_region ON price_history(region_code);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_price_history_slug_region_date ON price_history(slug, region_code, recorded_at);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for game_images
DROP TRIGGER IF EXISTS update_game_images_updated_at ON game_images;
CREATE TRIGGER update_game_images_updated_at
    BEFORE UPDATE ON game_images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for price history with min/max/avg per game
CREATE OR REPLACE VIEW price_stats AS
SELECT
    slug,
    region_code,
    MIN(price_brl) as min_price_brl,
    MAX(price_brl) as max_price_brl,
    AVG(price_brl)::DECIMAL(10,2) as avg_price_brl,
    MIN(recorded_at) as first_recorded,
    MAX(recorded_at) as last_recorded,
    COUNT(*) as total_records
FROM price_history
GROUP BY slug, region_code;
