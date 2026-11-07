\set ON_ERROR_STOP on

BEGIN;

\ir brand.sql
\ir category.sql
\ir seller.sql
\ir customer.sql
\ir products.sql
\ir order.sql
\ir order_item.sql
\ir promotion.sql
\ir promotion_product.sql

COMMIT;
