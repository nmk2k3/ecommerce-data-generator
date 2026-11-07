CREATE TABLE IF NOT EXISTS public.brand (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
