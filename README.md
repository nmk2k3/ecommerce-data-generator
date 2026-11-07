# Ecommerce Data Generator

## Khởi tạo toàn bộ schema

```bash
docker compose up -d --wait
```

Khi volume dữ liệu PostgreSQL còn trống, database tự chạy `sql/init.sql` để
tạo tất cả bảng và 5 partition tháng 01–05/2025 theo đúng thứ tự khóa ngoại.
Toàn bộ schema chạy trong một transaction; lỗi sẽ rollback và dừng khởi tạo.

Với database đã chạy, sau khi cập nhật container bằng lệnh trên, có thể tạo
toàn bộ schema bằng một lệnh:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /schemas/init.sql'
```

Các file dùng `CREATE TABLE IF NOT EXISTS`, có thể chạy lại để tạo bảng còn
thiếu. Lệnh này không sửa kiểu cột hoặc bổ sung ràng buộc cho bảng đã tồn tại.
PostgreSQL chỉ tự init khi volume dữ liệu còn trống, không chạy lại khi restart.

## Kết nối PostgreSQL

```bash
cp .env.example .env
docker compose up -d --wait
uv sync
uv run ecommerce-data-generator
```

Chỉnh các biến `POSTGRES_*` trong `.env` nếu cần. Biến môi trường đã được
thiết lập sẽ được ưu tiên hơn giá trị trong `.env`.

Sử dụng kết nối trong Python:

```python
from ecommerce_data_generator.db import get_connection

with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print(cursor.fetchone())
```

Kết nối tự đóng khi thoát khối `with`; transaction được commit khi thành công
hoặc rollback khi có lỗi.

## Chạy toàn bộ Faker bằng một lệnh

Sau khi khởi tạo schema và cấu hình kết nối PostgreSQL:

```bash
uv sync
uv run generate-all
```

Lệnh chạy theo thứ tự: brand (20), category (25), seller (50), customer (30.000),
products (3.000), promotion (30), promotion_product (500). Chưa có generator
cho order và order_item. Số dòng là mặc định của từng generator; số dòng thực tế
thêm có thể ít hơn nếu generator bỏ qua dữ liệu trùng đã tồn tại.

Mỗi generator commit riêng. Nếu một bước lỗi, lệnh dừng; các bước đã thành công
vẫn giữ dữ liệu. Chạy lại không xóa dữ liệu cũ, các generator vẫn hoạt động như
khi chạy từng lệnh riêng. Đổi số lượng từng bảng bằng lệnh riêng với `--count`.

## Tạo bảng brand

Áp dụng schema vào PostgreSQL đang chạy trong Docker:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/brand.sql
```

Bảng `public.brand` có `brand_id SERIAL` làm khóa chính, `brand_name VARCHAR(100)`
bắt buộc và duy nhất, `country VARCHAR(50)` cho phép `NULL`. Các cột audit gồm:

- `created_at`: `TIMESTAMP`, mặc định thời điểm tạo.
- `created_by`, `updated_by`, `deleted_by`: `VARCHAR(50)`, cho phép `NULL`.
- `updated_at`, `deleted_at`: `TIMESTAMP`, cho phép `NULL`.
- `is_deleted`: `BOOLEAN`, mặc định `false`.

Ứng dụng cần gán thông tin audit khi cập nhật hoặc xóa mềm bản ghi.
File SQL tạo bảng nếu chưa tồn tại; không thay đổi cấu trúc bảng đã có.

## Sinh dữ liệu brand bằng Faker

Sau khi khởi tạo schema và cấu hình kết nối PostgreSQL:

```bash
uv sync
uv run generate-brands --count 20
```

Nếu bỏ `--count`, lệnh mặc định sinh 20 dòng. `brand_id` do PostgreSQL tự tăng.
Tên brand dùng `fake.unique.company()`, quốc gia dùng `fake.country()`;
các giá trị vượt giới hạn độ dài được sinh lại. Tên đã tồn tại trong database
được bỏ qua, nên số dòng thêm thực tế có thể ít hơn số yêu cầu; lệnh in kết quả.

`created_at` nằm trong năm 2024, `updated_at` từ thời điểm tạo đến hiện tại.
`created_by`, `updated_by` dùng `fake.user_name()`.
`is_deleted` dùng `fake.boolean()` với xác suất mặc định, không ép tỷ lệ số dòng.
Chỉ các dòng xóa mềm mới có `deleted_at` và `deleted_by`; thời điểm xóa không
sớm hơn thời điểm cập nhật. Các dòng còn hoạt động để hai cột này là `NULL`.

## Tạo bảng category

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/category.sql
```

Bảng `public.category` có `category_id SERIAL` làm khóa chính,
`category_name VARCHAR(100)` bắt buộc và duy nhất, `parent_category_id BIGINT`
tham chiếu tới `category_id` của bảng này và cho phép `NULL` cho danh mục gốc.
`level SMALLINT` có ràng buộc `CHECK (level IN (1, 2))` và cho phép `NULL`.
Bảy cột audit giống bảng `brand`, dùng `TIMESTAMP` cho các cột thời gian.

## Sinh dữ liệu category bằng Faker

```bash
uv sync
uv run generate-categories
```

Lệnh tạo 25 category từ danh sách cố định: 5 danh mục chính (`level=1`,
`parent_category_id=NULL`) và 20 danh mục con (`level=2`), mỗi danh mục chính
có 4 danh mục con. ID cha được lấy từ database, không gán cứng.

| Danh mục chính | Danh mục con |
|---|---|
| Electronics | Smartphones, Laptops, Headphones, Cameras |
| Fashion | Clothing, Shoes, Bags, Accessories |
| Home & Living | Furniture, Kitchenware, Home Decor, Bedding |
| Beauty | Skincare, Makeup, Haircare, Fragrances |
| Sports | Fitness Equipment, Sportswear, Outdoor Gear, Sports Accessories |

Các cột audit sinh giống brand: `created_at` trong năm 2024,
`is_deleted` dùng `fake.boolean()`, chỉ dòng xóa mềm có thông tin xóa.
Chạy lại sẽ bỏ qua tên đã tồn tại và giữ nguyên audit. Nếu tên đã có nhưng
khác cấp hoặc khác danh mục cha, lệnh báo lỗi và rollback toàn bộ lần chạy.

## Tạo bảng seller

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/seller.sql
```

Bảng `public.seller` có `seller_id SERIAL` làm khóa chính,
`seller_name VARCHAR(150)` bắt buộc, `join_date DATE`, `country VARCHAR(50)`.
`seller_type VARCHAR(50)` chỉ nhận `Official` hoặc `Marketplace`;
`rating DECIMAL(2, 1)` nằm trong khoảng từ 0 đến 5.
Các cột nghiệp vụ ngoài `seller_id` và `seller_name` cho phép `NULL`.
Bảy cột audit giống bảng `brand`, dùng `TIMESTAMP` cho các cột thời gian.

## Sinh dữ liệu seller bằng Faker

```bash
uv sync
uv run generate-sellers
```

Mặc định tạo 50 seller với `Faker("vi_VN")`, `country` cố định `Vietnam`.
Có thể đổi số dòng bằng `--count`. Mỗi lần chạy thêm một lô dữ liệu mới.
`seller_id` do PostgreSQL tự tăng, tên seller tối đa 150 ký tự.
`join_date` nằm trong năm 2024; `created_at` từ đầu ngày tham gia đến hết năm 2024.
`seller_type` chọn giữa `Official` và `Marketplace`, rating từ 0 đến 5 với
một chữ số thập phân, dùng số thực Python (`float`).
Các cột audit còn lại giống brand: `is_deleted` dùng `fake.boolean()`,
chỉ dòng xóa mềm có thông tin xóa và thời gian xóa không sớm hơn cập nhật.

## Tạo bảng customer

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/customer.sql
```

Bảng `public.customer` có `customer_id SERIAL` làm khóa chính,
`customer_name VARCHAR(150)` bắt buộc, `email VARCHAR(150)` và
`phone VARCHAR(20)` có ràng buộc duy nhất riêng cho từng cột.
`gender VARCHAR(10)` chỉ nhận `Male` hoặc `Female`,
`address VARCHAR(225)`, `city VARCHAR(100)`.
Các cột nghiệp vụ ngoài `customer_id` và `customer_name` cho phép `NULL`.
Bảy cột audit giống bảng `brand`: thời gian dùng `TIMESTAMP`, các cột `*_by`
dùng `VARCHAR(50)`.

## Sinh dữ liệu customer bằng Faker

```bash
uv sync
uv run generate-customers
```

Mặc định sinh 30.000 customer với `Faker("vi_VN")`, có thể đổi bằng `--count`.
Tên được sinh theo giới tính `Male` hoặc `Female`. Email dùng một đối tượng
`Faker("en_US")` riêng với `unique.email()` để đủ giá trị duy nhất cho 30.000 dòng;
locale `vi_VN` có tập email quá nhỏ. Số điện thoại dùng `fake.unique.phone_number()`.
Email và số điện thoại không trùng trong lô sinh.
Giá trị vượt độ dài cột được sinh lại. Địa chỉ dùng `fake.street_address()`
chỉ gồm số nhà và đường; thành phố dùng `fake.city()` riêng,
không bảo đảm đường thực tế thuộc thành phố đó.

`created_at` nằm trong năm 2024; các cột audit còn lại giống brand.
`customer_id` do PostgreSQL tự tăng. Email hoặc số điện thoại trùng với database
được bỏ qua; lệnh in số dòng thực tế thêm và số dòng bỏ qua. Mỗi lần chạy sinh
một lô mới, không xóa hay cập nhật dữ liệu cũ. Chưa sinh dữ liệu order.

## Tạo bảng products

Tạo các bảng `category`, `brand`, `seller` trước, sau đó chạy:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/products.sql
```

Bảng `public.products` có `product_id SERIAL` làm khóa chính,
`product_name VARCHAR(200)` bắt buộc. Các cột `category_id`, `brand_id`,
`seller_id` dùng `INT`, là khóa ngoại tới các bảng tương ứng.
`price DECIMAL(12, 2)` phải lớn hơn 0, `stock_qty INT` phải từ 0 trở lên,
`rating DECIMAL(2, 1)` nằm trong khoảng từ 0 đến 5.
`is_active BOOLEAN` mặc định `true`.
Các cột nghiệp vụ ngoài `product_id` và `product_name` cho phép `NULL`.
Bảy cột audit giống các bảng trước: thời gian dùng `TIMESTAMP`,
các cột `*_by` dùng `VARCHAR(50)`.

## Sinh dữ liệu products bằng Faker

Sau khi có dữ liệu category, brand và seller:

```bash
uv sync
uv run generate-products
```

Mặc định tạo 3.000 product; có thể đổi bằng `--count`. Tên dùng
`fake.catch_phrase()`, giá dùng `fake.random.uniform(100000, 50000000)`
và để PostgreSQL làm tròn về hai chữ số thập phân khi lưu, tồn kho dùng
`fake.random_int(min=0, max=500)`. Rating từ 0 đến 5, một chữ số thập phân.

Khóa ngoại được chọn bằng Faker từ category cấp 2, brand và seller chưa xóa mềm.
Chỉ chọn bản ghi có thời điểm tạo không muộn hơn `2024-12-31 23:59:59`.
Nếu thiếu bất kỳ nhóm nào, lệnh báo lỗi và không ghi dữ liệu.
`created_at` nằm từ 01/06/2024 đến hết năm 2024, không sớm hơn thời điểm tạo
các bản ghi được tham chiếu. Audit giống brand; product xóa mềm luôn có
`is_active=False`, các product còn lại dùng `fake.boolean()` cho `is_active`.
Mỗi lần chạy thêm một lô dữ liệu mới, không xóa dữ liệu cũ.

## Tạo bảng order

Tạo bảng `customer` trước, sau đó chạy:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/order.sql
```

Bảng `public."order"` có `order_id SERIAL` làm khóa chính,
`customer_id INT` là khóa ngoại tới `customer`, `order_date TIMESTAMP`.
`status VARCHAR(20)` chỉ nhận `PLACED`, `PAID`, `SHIPPED`, `DELIVERED`,
`CANCELLED`, `RETURNED`; `total_amount DECIMAL(12, 2)` phải từ 0 trở lên.
Bảy cột audit giống các bảng trước, thêm ràng buộc `created_at >= order_date`.
Các cột nghiệp vụ ngoài `order_id` cho phép `NULL`.
Tên bảng `"order"` cần dấu nháy kép khi truy vấn vì `ORDER` là từ khóa SQL.

## Tạo bảng order_item

Tạo các bảng phụ thuộc trước theo thứ tự: `customer`, `brand`, `category`,
`seller`, `products`, `order`, sau đó chạy:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/order_item.sql
```

Bảng `public.order_item` partition theo `RANGE (order_date)` với khóa chính
`(order_item_id, order_date)`, `order_item_id SERIAL`, `order_date TIMESTAMP`.
`order_id INT` và `product_id INT` bắt buộc, có khóa ngoại tới các bảng tương ứng.
Khóa ngoại ghép `(order_id, order_date)` bảo đảm ngày khớp với đơn hàng;
schema `order` có `UNIQUE (order_id, order_date)` để hỗ trợ ràng buộc này.
Ứng dụng cần sao chép `order_date` từ đơn hàng khi INSERT.

`quantity INT` và `unit_price DECIMAL(12, 2)` bắt buộc và phải lớn hơn 0.
`subtotal DECIMAL(12, 2)` tự tính bằng `quantity * unit_price`, không truyền
giá trị cho cột này khi INSERT hoặc UPDATE.
Bảy cột audit giống `order`, gồm các CHECK `created_at >= order_date`,
`updated_at >= created_at`, `deleted_at >= created_at`.

File SQL tạo sẵn 5 partition tháng từ tháng 01/2025 đến hết tháng 05/2025
(từ `2025-01-01` đến trước `2025-06-01`). Dữ liệu ngoài khoảng này bị từ chối;
cần tạo thêm partition nếu mở rộng thời gian.

## Tạo bảng promotion

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/promotion.sql
```

Bảng `public.promotion` có `promotion_id SERIAL` làm khóa chính,
`promotion_name VARCHAR(100)` bắt buộc, `promotion_type VARCHAR(50)`.
`discount_type VARCHAR(20)` chỉ nhận `percentage` hoặc `fixed_amount`.
`discount_value NUMERIC(10, 2)` phải lớn hơn 0; với `percentage` không vượt quá 100.
`start_date DATE` không sớm hơn `DATE(created_at)`;
`end_date DATE` không sớm hơn `start_date`.
Các cột nghiệp vụ ngoài `promotion_id` và `promotion_name` cho phép `NULL`.
Bảy cột audit giống các bảng trước: thời gian dùng `TIMESTAMP`,
các cột `*_by` dùng `VARCHAR(50)`.

## Sinh dữ liệu promotion bằng Faker

```bash
uv sync
uv run generate-promotions
```

Mặc định tạo 30 promotion; có thể đổi bằng `--count`. Tên dùng `fake.catch_phrase()`,
loại chọn trong `product`, `category`, `seller`, `flash_sale`.
`discount_type` dùng `percentage` hoặc `fixed_amount`: mức giảm phần trăm từ
1 đến 100, mức giảm cố định từ 10.000 đến 500.000, đều dùng `fake.random_int()`.

`start_date` từ 01/01 đến 31/05/2025; `end_date` sau ngày bắt đầu 30–50 ngày,
có thể sang tháng 7/2025. `created_at` từ 01/12/2024 đến 31/01/2025,
với ngày tạo không sau ngày bắt đầu khuyến mãi. Không ép số campaign mỗi tháng.
Audit còn lại giống brand; chỉ promotion xóa mềm có thông tin xóa.
Mỗi lần chạy thêm một lô mới, không xóa hay cập nhật dữ liệu cũ.

## Tạo bảng promotion_product

Tạo bảng `promotion` và `products` cùng các bảng phụ thuộc trước, sau đó chạy:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/promotion_product.sql
```

Bảng `public.promotion_product` có `promo_product_id SERIAL` làm khóa chính,
`promotion_id INT` là khóa ngoại tới `promotion(promotion_id)`,
`product_id INT` là khóa ngoại tới `products(product_id)`.
Hai cột khóa ngoại cho phép `NULL`.
Bảy cột audit giống các bảng trước: thời gian dùng `TIMESTAMP`,
các cột `*_by` dùng `VARCHAR(50)`, `is_deleted` mặc định `false`.

## Sinh dữ liệu promotion_product bằng Faker

Sau khi có dữ liệu promotion và products:

```bash
uv sync
uv run generate-promotion-products
```

Mặc định tạo 500 liên kết; có thể đổi bằng `--count`. Phân bổ đều giữa các
promotion đủ điều kiện: với 30 promotion, 20 promotion có 17 product và
10 promotion có 16 product. Product được chọn bằng `fake.random_elements()`
với `unique=True`, không trùng cặp `(promotion_id, product_id)` trong mỗi lô.

`created_at` nằm trong 01/01–31/05/2025, không sớm hơn thời điểm tạo promotion
và product. Bản ghi nguồn được chọn theo thời điểm tạo, gồm cả bản ghi đã xóa mềm;
không chọn nguồn tạo sau `2025-05-31 23:59:59`. Nếu thiếu nguồn hoặc không đủ
cặp khác nhau, lệnh báo lỗi trước khi ghi dữ liệu. Audit giống các bảng trước.
Mỗi lần chạy thêm một lô mới; cặp liên kết có thể trùng với lô đã chạy trước đó.
