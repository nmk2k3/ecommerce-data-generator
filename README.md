# Ecommerce Data Generator

Generate sample ecommerce data with Python, Faker, and PostgreSQL.

## Quick start

Requires Python 3.12+, uv, and Docker Compose.

```bash
cp .env.example .env
uv sync
docker compose up -d --wait
uv run generate-all
```

Edit `.env` to change the database connection. Existing environment variables
take priority over `.env`. PostgreSQL creates the schema automatically on the
first start with an empty data volume.

## Generator commands

Run these in dependency order when generating tables individually:

```bash
uv run generate-brands --count 20
uv run generate-categories
uv run generate-sellers --count 50
uv run generate-customers --count 30000
uv run generate-products --count 3000
uv run generate-promotions --count 30
uv run generate-promotion-products --count 500
```

These are the default counts. Categories use a fixed hierarchy of 5 parents and
20 children. Order and order-item generators are not implemented yet.

Each generator commits separately. If `generate-all` fails, earlier successful
steps remain committed. Running again preserves existing data: brand and category
names and customer emails or phone numbers are skipped on conflict; other
records are appended. Duplicate promotion-product pairs cause an error and roll
back the entire promotion-product batch.

## Database commands

Open a SQL session:

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Create missing tables in an existing database:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /schemas/init.sql'
```

Schema initialization runs in one transaction. It does not migrate existing
tables. The SQL files are in `sql/`; order-item partitions cover January–May 2025.

Stop PostgreSQL while keeping its data:

```bash
docker compose down
```

## Data conventions

- Brands, categories, sellers, and customers are created in 2024; products are
  created in June–December 2024.
- Promotions start in January–May 2025; promotion-product links are created in
  that period. Audit updates and deletions may extend to the current time.
- New child categories cannot predate their parent. A parent created after the
  2024 generation window causes the category generator to fail.
- Products require non-deleted level-2 categories, brands, and sellers.
  Promotion-product links may reference soft-deleted records.
- Only soft-deleted records receive deletion audit values. Existing records
  keep their audit values when skipped.

## Code checks

```bash
uv run python -m unittest discover -s tests -v
uv run ruff check .
uv run ruff format --check .
```
