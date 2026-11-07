CREATE TABLE IF NOT EXISTS public.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT REFERENCES public.category(category_id),
    brand_id INT REFERENCES public.brand(brand_id),
    seller_id INT REFERENCES public.seller(seller_id),
    price DECIMAL(12, 2) CHECK (price > 0),
    stock_qty INT CHECK (stock_qty >= 0),
    rating DECIMAL(2, 1) CHECK (rating BETWEEN 0 AND 5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
