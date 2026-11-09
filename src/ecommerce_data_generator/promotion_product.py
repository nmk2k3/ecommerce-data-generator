import argparse
from datetime import datetime
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class PromotionProduct(TypedDict):
    promotion_id: int
    product_id: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_promotion_products(
    count: int,
    promotions: list[tuple[int, datetime]],
    products: list[tuple[int, datetime]],
) -> list[PromotionProduct]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    start = datetime(2025, 1, 1)
    end = datetime(2025, 5, 31, 23, 59, 59)
    promotions = [row for row in promotions if row[1] <= end]
    products = [row for row in products if row[1] <= end]
    for name, rows, command in (
        ("promotions", promotions, "generate-promotions"),
        ("products", products, "generate-products"),
    ):
        if not rows:
            raise ValueError(f"No eligible {name}. Run 'uv run {command}' first.")
    if count > len(promotions) * len(products):
        raise ValueError(
            f"Only {len(promotions) * len(products)} distinct pairs available. "
            "Reduce '--count' or generate more promotions/products."
        )

    fake = Faker()
    links: list[PromotionProduct] = []
    now = datetime.now()
    # Spread links evenly; earlier promotions receive any remainder.
    per_promotion, remainder = divmod(count, len(promotions))
    for index, (promotion_id, promotion_created_at) in enumerate(promotions):
        product_count = per_promotion + (1 if index < remainder else 0)
        if product_count == 0:
            continue
        # Sampling without replacement prevents duplicate pairs within this batch.
        selected_products = fake.random_elements(
            elements=products, length=product_count, unique=True
        )
        for product_id, product_created_at in selected_products:
            earliest_created_at = max(start, promotion_created_at, product_created_at)
            # Faker may drop microseconds; preserve the exact lower bound.
            created_at = max(
                earliest_created_at,
                fake.date_time_between(start_date=earliest_created_at, end_date=end),
            )
            created_by = fake.user_name()
            updated_at = max(
                created_at,
                fake.date_time_between(start_date=created_at, end_date=now),
            )
            updated_by = fake.user_name()
            is_deleted = fake.boolean()
            deleted_at = (
                max(
                    updated_at,
                    fake.date_time_between(start_date=updated_at, end_date=now),
                )
                if is_deleted
                else None
            )
            deleted_by = fake.user_name() if is_deleted else None
            links.append(
                {
                    "promotion_id": promotion_id,
                    "product_id": product_id,
                    "created_at": created_at,
                    "created_by": created_by,
                    "updated_at": updated_at,
                    "updated_by": updated_by,
                    "deleted_at": deleted_at,
                    "deleted_by": deleted_by,
                    "is_deleted": is_deleted,
                }
            )
    return links


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate promotion-product links with Faker"
    )
    parser.add_argument(
        "--count", type=int, default=500, help="Number of links (default: 500)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    with get_connection() as connection, connection.cursor() as cursor:
        # Historical links intentionally include sources that are now soft-deleted.
        cursor.execute(
            "SELECT promotion_id, created_at FROM public.promotion ORDER BY promotion_id"
        )
        promotions = cursor.fetchall()
        cursor.execute(
            "SELECT product_id, created_at FROM public.products ORDER BY product_id"
        )
        products = cursor.fetchall()
        links = generate_promotion_products(args.count, promotions, products)
        cursor.executemany(
            """
                INSERT INTO public.promotion_product (
                    promotion_id, product_id, created_at, created_by,
                    updated_at, updated_by, deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(promotion_id)s, %(product_id)s, %(created_at)s, %(created_by)s,
                    %(updated_at)s, %(updated_by)s, %(deleted_at)s,
                    %(deleted_by)s, %(is_deleted)s
                )
                """,
            links,
        )
        inserted = cursor.rowcount
    print(f"Inserted {inserted} promotion-product links.")


if __name__ == "__main__":
    main()
