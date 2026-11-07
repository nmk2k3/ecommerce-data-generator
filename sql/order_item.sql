CREATE TABLE IF NOT EXISTS public.order_item (
    order_item_id SERIAL,
    order_id INT NOT NULL,
    product_id INT NOT NULL REFERENCES public.products(product_id),
    order_date TIMESTAMP NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price > 0),
    subtotal DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (order_item_id, order_date),
    FOREIGN KEY (order_id, order_date) REFERENCES public."order"(order_id, order_date),
    CHECK (created_at >= order_date),
    CHECK (updated_at >= created_at),
    CHECK (deleted_at >= created_at)
) PARTITION BY RANGE (order_date);

CREATE TABLE IF NOT EXISTS public.order_item_2025_01
    PARTITION OF public.order_item
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS public.order_item_2025_02
    PARTITION OF public.order_item
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE IF NOT EXISTS public.order_item_2025_03
    PARTITION OF public.order_item
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE IF NOT EXISTS public.order_item_2025_04
    PARTITION OF public.order_item
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE IF NOT EXISTS public.order_item_2025_05
    PARTITION OF public.order_item
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
