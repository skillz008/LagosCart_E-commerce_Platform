PRAGMA foreign_keys=ON;
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
CREATE TABLE categories(category_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories, sku TEXT NOT NULL UNIQUE, name TEXT NOT NULL, price_kobo INTEGER NOT NULL CHECK(price_kobo>=0), stock INTEGER NOT NULL CHECK(stock>=0));
CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers, ordered_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','paid','shipped','cancelled')));
CREATE TABLE order_items(order_id INTEGER NOT NULL REFERENCES orders, product_id INTEGER NOT NULL REFERENCES products, quantity INTEGER NOT NULL CHECK(quantity>0), unit_price_kobo INTEGER NOT NULL CHECK(unit_price_kobo>=0), PRIMARY KEY(order_id,product_id));
CREATE TABLE payments(payment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL UNIQUE REFERENCES orders, reference TEXT NOT NULL UNIQUE, amount_kobo INTEGER NOT NULL CHECK(amount_kobo>0), status TEXT NOT NULL CHECK(status IN ('captured','refunded')));
CREATE TABLE deliveries(delivery_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL UNIQUE REFERENCES orders, address TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','dispatched','delivered')));
