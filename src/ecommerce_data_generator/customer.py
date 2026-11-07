import argparse
from datetime import datetime
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection


class Customer(TypedDict):
    customer_name: str
    email: str
    phone: str
    gender: str
    address: str
    city: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_customers(count: int) -> list[Customer]:
    if count < 1:
        raise ValueError("count must be greater than zero")

    # Vietnamese locale for customer names, phone numbers, addresses and audit data.
    fake = Faker("vi_VN")
    # vi_VN has too few unique emails for 30,000 customers; use en_US for emails only.
    email_fake = Faker("en_US")
    customers: list[Customer] = []
    now = datetime.now()
    for _ in range(count):
        gender = fake.random_element(elements=("Male", "Female"))
        name_provider = fake.name_male if gender == "Male" else fake.name_female
        customer_name = name_provider()
        while len(customer_name) > 150:
            customer_name = name_provider()

        email = email_fake.unique.email()
        while len(email) > 150:
            email = email_fake.unique.email()

        phone = fake.unique.phone_number()
        while len(phone) > 20:
            phone = fake.unique.phone_number()

        address = fake.street_address()
        while len(address) > 225:
            address = fake.street_address()

        city = fake.city()
        while len(city) > 100:
            city = fake.city()

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

        customers.append(
            {
                "customer_name": customer_name,
                "email": email,
                "phone": phone,
                "gender": gender,
                "address": address,
                "city": city,
                "created_at": created_at,
                "created_by": created_by,
                "updated_at": updated_at,
                "updated_by": updated_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "is_deleted": is_deleted,
            }
        )
    return customers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Vietnam-based customers with Faker"
    )
    parser.add_argument(
        "--count", type=int, default=30_000, help="Number of customers (default: 30000)"
    )
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be greater than zero")

    customers = generate_customers(args.count)
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(
            """
                INSERT INTO public.customer (
                    customer_name, email, phone, gender, address, city,
                    created_at, created_by, updated_at, updated_by,
                    deleted_at, deleted_by, is_deleted
                ) VALUES (
                    %(customer_name)s, %(email)s, %(phone)s, %(gender)s,
                    %(address)s, %(city)s, %(created_at)s, %(created_by)s,
                    %(updated_at)s, %(updated_by)s, %(deleted_at)s,
                    %(deleted_by)s, %(is_deleted)s
                )
                ON CONFLICT DO NOTHING
                """,
            customers,
        )
        inserted = cursor.rowcount
    print(
        f"Inserted {inserted} Vietnam-based customers; "
        f"skipped {args.count - inserted} existing emails or phone numbers."
    )


if __name__ == "__main__":
    main()
