CREATE TABLE IF NOT EXISTS public.promotion (
    promotion_id SERIAL PRIMARY KEY,
    promotion_name VARCHAR(100) NOT NULL,
    promotion_type VARCHAR(50),
    discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value NUMERIC(10, 2) CHECK (
        discount_value > 0 AND (discount_type = 'fixed_amount' OR discount_value <= 100)
    ),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (start_date >= DATE(created_at)),
    CHECK (end_date >= start_date)
);
