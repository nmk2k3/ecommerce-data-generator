import argparse

from ecommerce_data_generator import (
    brand,
    category,
    customer,
    products,
    promotion,
    promotion_product,
    seller,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all available Faker generators in dependency order"
    )
    parser.parse_args()

    for module in (
        brand,
        category,
        seller,
        customer,
        products,
        promotion,
        promotion_product,
    ):
        print(f"Generating {module.__name__.rsplit('.', 1)[-1]}...", flush=True)
        module.main()


if __name__ == "__main__":
    main()
