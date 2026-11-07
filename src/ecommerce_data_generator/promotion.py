import argparse
from datetime import date, datetime, time, timedelta
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class Promotion(TypedDict):
    promotion_name: str
    promotion_type: str
    discount_type: str
    discount_value: int
    start_date: date
    end_date: date
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_promotions(count: int) -> list[Promotion]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    fake = Faker()
    promotions: list[Promotion] = []
    now = datetime.now()
    for _ in range(count):
        promotion_name = fake.catch_phrase()
        while len(promotion_name) > 100:
            promotion_name = fake.catch_phrase()

        promotion_type = fake.random_element(
            elements=("product", "category", "seller", "flash_sale")
        )
        discount_type = fake.random_element(elements=("percentage", "fixed_amount"))
        discount_value = (
            fake.random_int(min=1, max=100)
            if discount_type == "percentage"
            else fake.random_int(min=10_000, max=500_000)
        )
        start_date = fake.date_between(
            start_date=date(2025, 1, 1), end_date=date(2025, 5, 31)
        )
        end_date = start_date + timedelta(days=fake.random_int(min=30, max=50))
        # The schema requires the creation date to be on or before the start date.
        created_at = fake.date_time_between(
            start_date=datetime(2024, 12, 1),
            end_date=min(
                datetime(2025, 1, 31, 23, 59, 59),
                datetime.combine(start_date, time.max),
            ),
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

        promotions.append(
            {
                "promotion_name": promotion_name,
                "promotion_type": promotion_type,
                "discount_type": discount_type,
                "discount_value": discount_value,
                "start_date": start_date,
                "end_date": end_date,
                "created_at": created_at,
                "created_by": created_by,
                "updated_at": updated_at,
                "updated_by": updated_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "is_deleted": is_deleted,
            }
        )
    return promotions


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate promotion data with Faker")
    parser.add_argument(
        "--count", type=int, default=30, help="Number of promotions (default: 30)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    promotions = generate_promotions(args.count)
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(
            """
                INSERT INTO public.promotion (
                    promotion_name, promotion_type, discount_type, discount_value,
                    start_date, end_date, created_at, created_by, updated_at,
                    updated_by, deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(promotion_name)s, %(promotion_type)s, %(discount_type)s,
                    %(discount_value)s, %(start_date)s, %(end_date)s, %(created_at)s,
                    %(created_by)s, %(updated_at)s, %(updated_by)s, %(deleted_at)s,
                    %(deleted_by)s, %(is_deleted)s
                )
                """,
            promotions,
        )
        inserted = cursor.rowcount
    print(f"Inserted {inserted} promotions.")


if __name__ == "__main__":
    main()
