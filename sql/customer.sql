CREATE TABLE IF NOT EXISTS public.customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female')),
    address VARCHAR(225),
    city VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_at TIMESTAMP,
    updated_by VARCHAR(50),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(50),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
