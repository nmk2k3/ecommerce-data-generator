CREATE TABLE IF NOT EXISTS public.seller (
    seller_id SERIAL PRIMARY KEY,
    seller_name VARCHAR(150) NOT NULL,
    join_date DATE,
    seller_type VARCHAR(50) CHECK (seller_type IN ('Official', 'Marketplace')),
    rating DECIMAL(2, 1) CHECK (rating BETWEEN 0 AND 5),
    country VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
