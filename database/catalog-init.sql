CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    image_url TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_code ON products(code);
CREATE INDEX idx_products_stock ON products(stock_quantity);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

INSERT INTO products (code, name, image_url, price, stock_quantity) VALUES
    ('PROD-001', 'Laptop Dell XPS 15', 'https://via.placeholder.com/300x300.png?text=Laptop', 1299.99, 15),
    ('PROD-002', 'Wireless Mouse Logitech MX Master', 'https://via.placeholder.com/300x300.png?text=Mouse', 99.99, 50),
    ('PROD-003', 'Mechanical Keyboard Keychron K2', 'https://via.placeholder.com/300x300.png?text=Keyboard', 89.99, 30),
    ('PROD-004', 'USB-C Hub 7-in-1', 'https://via.placeholder.com/300x300.png?text=USB-Hub', 49.99, 100),
    ('PROD-005', 'Monitor LG UltraWide 34"', 'https://via.placeholder.com/300x300.png?text=Monitor', 599.99, 20),
    ('PROD-006', 'Webcam Logitech C920', 'https://via.placeholder.com/300x300.png?text=Webcam', 79.99, 45),
    ('PROD-007', 'Headphones Sony WH-1000XM4', 'https://via.placeholder.com/300x300.png?text=Headphones', 349.99, 25),
    ('PROD-008', 'External SSD Samsung T7 1TB', 'https://via.placeholder.com/300x300.png?text=SSD', 129.99, 60)
ON CONFLICT (code) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '✅ Catalog database schema initialized successfully!';
    RAISE NOTICE '📦 Inserted 8 sample products';
END $$;
