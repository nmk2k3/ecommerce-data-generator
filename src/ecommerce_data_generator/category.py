from datetime import datetime
from typing import TypedDict

from faker import Faker

from ecommerce_data_generator.db import get_connection

CATEGORIES = {
    "Electronics": ("Smartphones", "Laptops", "Headphones", "Cameras"),
    "Fashion": ("Clothing", "Shoes", "Bags", "Accessories"),
    "Home & Living": ("Furniture", "Kitchenware", "Home Decor", "Bedding"),
    "Beauty": ("Skincare", "Makeup", "Haircare", "Fragrances"),
    "Sports": ("Fitness Equipment", "Sportswear", "Outdoor Gear", "Sports Accessories"),
}


class Category(TypedDict):
    category_name: str
    parent_category_id: int | None
    level: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    deleted_at: datetime | None
    deleted_by: str | None
    is_deleted: bool


def generate_category(
    name: str,
    parent_id: int | None,
    fake: Faker,
    parent_created_at: datetime | None = None,
) -> Category:
    now = datetime.now()
    # Keep children within the fixture year without predating their parent.
    start = max(datetime(2024, 1, 1), parent_created_at or datetime(2024, 1, 1))
    end = datetime(2024, 12, 31, 23, 59, 59)
    if start > end:
        raise ValueError("Parent category was created after the 2024 generation window")
    created_at = max(
        start,
        fake.date_time_between(start_date=start, end_date=end),
    )
    created_by = fake.user_name()
    updated_at = max(
        created_at, fake.date_time_between(start_date=created_at, end_date=now)
    )
    updated_by = fake.user_name()
    is_deleted = fake.boolean()
    deleted_at = (
        max(updated_at, fake.date_time_between(start_date=updated_at, end_date=now))
        if is_deleted
        else None
    )
    deleted_by = fake.user_name() if is_deleted else None

    return {
        "category_name": name,
        "parent_category_id": parent_id,
        "level": 1 if parent_id is None else 2,
        "created_at": created_at,
        "created_by": created_by,
        "updated_at": updated_at,
        "updated_by": updated_by,
        "deleted_at": deleted_at,
        "deleted_by": deleted_by,
        "is_deleted": is_deleted,
    }


def main() -> None:
    fake = Faker()
    inserted = 0
    skipped = 0
    with get_connection() as connection, connection.cursor() as cursor:
        for parent_name, children in CATEGORIES.items():
            parent_id: int | None = None
            parent_created_at: datetime | None = None
            for name in (parent_name, *children):
                category = generate_category(name, parent_id, fake, parent_created_at)
                cursor.execute(
                    """
                        INSERT INTO public.category (
                            category_name, parent_category_id, level,
                            created_at, created_by, updated_at, updated_by,
                            deleted_at, deleted_by, is_deleted
                        ) VALUES (
                            %(category_name)s, %(parent_category_id)s, %(level)s,
                            %(created_at)s, %(created_by)s, %(updated_at)s, %(updated_by)s,
                            %(deleted_at)s, %(deleted_by)s, %(is_deleted)s
                        )
                        ON CONFLICT (category_name) DO NOTHING
                        RETURNING category_id, created_at
                        """,
                    category,
                )
                row = cursor.fetchone()
                if row is None:
                    # Reuse existing rows only when their hierarchy matches.
                    cursor.execute(
                        """
                            SELECT category_id, created_at, parent_category_id, level
                            FROM public.category WHERE category_name = %s
                            """,
                        (name,),
                    )
                    row = cursor.fetchone()
                    if row is None or row[2:] != (parent_id, category["level"]):
                        raise ValueError(
                            f"Existing category has a different hierarchy: {name}"
                        )
                    skipped += 1
                else:
                    inserted += 1
                if name == parent_name:
                    # Use stored values even if the parent insert was skipped.
                    parent_id = row[0]
                    parent_created_at = row[1]
    print(f"Inserted {inserted} categories; skipped {skipped} existing names.")


if __name__ == "__main__":
    main()
