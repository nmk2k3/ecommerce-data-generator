CREATE TABLE IF NOT EXISTS public.category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    parent_category_id BIGINT REFERENCES public.category(category_id),
    level SMALLINT CHECK (level IN (1, 2)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
