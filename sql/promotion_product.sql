CREATE TABLE IF NOT EXISTS public.promotion_product (
    promo_product_id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES public.promotion(promotion_id),
    product_id INT REFERENCES public.products(product_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (promotion_id, product_id)
);
