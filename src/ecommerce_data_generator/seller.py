import argparse
from datetime import date, datetime, time
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class Seller(TypedDict):
    seller_name: str
    join_date: date
    seller_type: str
    rating: float
    country: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_sellers(count: int) -> list[Seller]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    fake = Faker("vi_VN")
    sellers: list[Seller] = []
    now = datetime.now()
    for _ in range(count):
        seller_name = fake.company()
        while len(seller_name) > 150:
            seller_name = fake.company()

        join_date = fake.date_between(
            start_date=date(2024, 1, 1), end_date=date(2024, 12, 31)
        )
        created_at = fake.date_time_between(
            start_date=datetime.combine(join_date, time.min),
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

        sellers.append(
            {
                "seller_name": seller_name,
                "join_date": join_date,
                "seller_type": fake.random_element(
                    elements=("Official", "Marketplace")
                ),
                "rating": fake.random_int(min=0, max=50) / 10,
                "country": "Vietnam",
                "created_at": created_at,
                "created_by": created_by,
                "updated_at": updated_at,
                "updated_by": updated_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "is_deleted": is_deleted,
            }
        )
    return sellers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Vietnam-based sellers with Faker"
    )
    parser.add_argument(
        "--count", type=int, default=50, help="Number of sellers (default: 50)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    sellers = generate_sellers(args.count)
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(
            """
                INSERT INTO public.seller (
                    seller_name, join_date, seller_type, rating, country,
                    created_at, created_by, updated_at, updated_by,
                    deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(seller_name)s, %(join_date)s, %(seller_type)s, %(rating)s,
                    %(country)s, %(created_at)s, %(created_by)s, %(updated_at)s,
                    %(updated_by)s, %(deleted_at)s, %(deleted_by)s, %(is_deleted)s
                )
                """,
            sellers,
        )
        inserted = cursor.rowcount
    print(f"Inserted {inserted} Vietnam-based sellers.")


if __name__ == "__main__":
    main()
