import argparse
from datetime import datetime
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class Brand(TypedDict):
    brand_name: str
    country: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_brands(count: int) -> list[Brand]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    fake = Faker()
    brands: list[Brand] = []
    now = datetime.now()
    for _ in range(count):
        brand_name = fake.unique.company()
        while len(brand_name) > 100:
            brand_name = fake.unique.company()

        country = fake.country()
        while len(country) > 50:
            country = fake.country()

        created_at = fake.date_time_between(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31, 23, 59, 59),
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

        brands.append(
            {
                "brand_name": brand_name,
                "country": country,
                "created_at": created_at,
                "created_by": created_by,
                "updated_at": updated_at,
                "updated_by": updated_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "is_deleted": is_deleted,
            }
        )
    return brands


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Faker data for public.brand")
    parser.add_argument(
        "--count", type=int, default=20, help="Number of brands (default: 20)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    brands = generate_brands(args.count)
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(
            """
                INSERT INTO public.brand (
                    brand_name, country, created_at, created_by,
                    updated_at, updated_by, deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(brand_name)s, %(country)s, %(created_at)s, %(created_by)s,
                    %(updated_at)s, %(updated_by)s, %(deleted_at)s,
                    %(deleted_by)s, %(is_deleted)s
                )
                ON CONFLICT (brand_name) DO NOTHING
                """,
            brands,
        )
        inserted = cursor.rowcount
    print(
        f"Inserted {inserted} brands; skipped {args.count - inserted} existing names."
    )


if __name__ == "__main__":
    main()
