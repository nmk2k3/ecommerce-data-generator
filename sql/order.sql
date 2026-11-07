CREATE TABLE IF NOT EXISTS public."order" (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES public.customer(customer_id),
    order_date TIMESTAMP,
    status VARCHAR(20) CHECK (
        status IN ('PLACED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')
    ),
    total_amount DECIMAL(12, 2) CHECK (total_amount >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (order_id, order_date),
    CHECK (created_at >= order_date),
    CHECK (updated_at >= created_at),
    CHECK (deleted_at >= created_at)
);
