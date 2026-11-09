import argparse
from datetime import datetime
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class Product(TypedDict):
    product_name: str
    category_id: int
    brand_id: int
    seller_id: int
    price: float
    stock_qty: int
    rating: float
    is_active: bool
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_products(
    count: int,
    categories: list[tuple[int, datetime]],
    brands: list[tuple[int, datetime]],
    sellers: list[tuple[int, datetime]],
) -> list[Product]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    start = datetime(2024, 6, 1)
    end = datetime(2024, 12, 31, 23, 59, 59)
    # Sources created later cannot be referenced by a product in this window.
    categories = [row for row in categories if row[1] <= end]
    brands = [row for row in brands if row[1] <= end]
    sellers = [row for row in sellers if row[1] <= end]
    for name, rows, command in (
        ("level-2 categories", categories, "generate-categories"),
        ("brands", brands, "generate-brands"),
        ("sellers", sellers, "generate-sellers"),
    ):
        if not rows:
            raise ValueError(f"No eligible {name}. Run 'uv run {command}' first.")

    fake = Faker()
    products: list[Product] = []
    now = datetime.now()
    for _ in range(count):
        category_id, category_created_at = fake.random_element(elements=categories)
        brand_id, brand_created_at = fake.random_element(elements=brands)
        seller_id, seller_created_at = fake.random_element(elements=sellers)
        product_name = fake.catch_phrase()
        while len(product_name) > 200:
            product_name = fake.catch_phrase()

        # A product must exist no earlier than any of its referenced records.
        earliest_created_at = max(
            start, category_created_at, brand_created_at, seller_created_at
        )
        # Faker may drop microseconds; max keeps created_at at or after the lower bound.
        created_at = max(
            earliest_created_at,
            fake.date_time_between(start_date=earliest_created_at, end_date=end),
        )
        created_by = fake.user_name()
        updated_at = fake.date_time_between(start_date=created_at, end_date=now)
        updated_by = fake.user_name()
        is_deleted = fake.boolean()
        deleted_at = (
            fake.date_time_between(start_date=updated_at, end_date=now)
            if is_deleted
            else None
        )
        deleted_by = fake.user_name() if is_deleted else None

        products.append(
            {
                "product_name": product_name,
                "category_id": category_id,
                "brand_id": brand_id,
                "seller_id": seller_id,
                "price": fake.random.uniform(100_000, 50_000_000),
                "stock_qty": fake.random_int(min=0, max=500),
                "rating": fake.random_int(min=0, max=50) / 10,
                "is_active": False if is_deleted else fake.boolean(),
                "created_at": created_at,
                "created_by": created_by,
                "updated_at": updated_at,
                "updated_by": updated_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "is_deleted": is_deleted,
            }
        )
    return products


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate product data with Faker")
    parser.add_argument(
        "--count", type=int, default=3_000, help="Number of products (default: 3000)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT category_id, created_at FROM public.category WHERE level = 2 AND NOT is_deleted"
        )
        categories = cursor.fetchall()
        cursor.execute(
            "SELECT brand_id, created_at FROM public.brand WHERE NOT is_deleted"
        )
        brands = cursor.fetchall()
        cursor.execute(
            "SELECT seller_id, created_at FROM public.seller WHERE NOT is_deleted"
        )
        sellers = cursor.fetchall()
        products = generate_products(args.count, categories, brands, sellers)
        cursor.executemany(
            """
                INSERT INTO public.products (
                    product_name, category_id, brand_id, seller_id,
                    price, stock_qty, rating, is_active,
                    created_at, created_by, updated_at, updated_by,
                    deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(product_name)s, %(category_id)s, %(brand_id)s, %(seller_id)s,
                    %(price)s, %(stock_qty)s, %(rating)s, %(is_active)s,
                    %(created_at)s, %(created_by)s, %(updated_at)s, %(updated_by)s,
                    %(deleted_at)s, %(deleted_by)s, %(is_deleted)s
                )
                """,
            products,
        )
        inserted = cursor.rowcount
    print(f"Inserted {inserted} products.")


if __name__ == "__main__":
    main()
