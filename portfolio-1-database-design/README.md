# Portfolio 1 — Database design and modelling (7 marks)

## Scope and business rules
One customer has zero or many orders; each order belongs to one customer. One category has zero or many products; each product has one category. Orders and products have a many-to-many relationship resolved by order_items. Each order has zero or one captured/refunded payment record and zero or one delivery. A draft order can initially have no lines, but the checkout workflow creates a line before commit. Customer email, SKU and payment reference are unique. Amounts use integer kobo (100 kobo = NGN 1) to avoid floating-point monetary calculations.

The payment simplification deliberately excludes instalments, multiple payment attempts and partial refunds. Deliveries use one address snapshot rather than an independently managed address book. Product category reassignment does not alter historical sale prices: order_items.unit_price_kobo is the actual sale price, not a redundant copy of the current catalogue price.

## Relational schema and dependencies
- customers(customer_id PK, name, email UNIQUE). customer_id -> name,email; email is an alternate key.
- categories(category_id PK, name UNIQUE). category_id -> name.
- products(product_id PK, category_id FK, sku UNIQUE, name, price_kobo, stock). product_id -> all non-key fields; sku is an alternate key.
- orders(order_id PK, customer_id FK, ordered_at, status). order_id -> customer_id,ordered_at,status.
- order_items(order_id PK/FK, product_id PK/FK, quantity, unit_price_kobo). (order_id,product_id) -> quantity,unit_price_kobo.
- payments(payment_id PK, order_id UNIQUE FK, reference UNIQUE, amount_kobo, status). Each candidate key determines all remaining attributes.
- deliveries(delivery_id PK, order_id UNIQUE FK, address, status). delivery_id and order_id are candidate keys.

## Normalisation
Start with an illustrative unnormalised Order(order_id,customer_name,email,items=[...],payment,...). This mixes repeating items, customer facts and order facts.
1NF: represent each item as a separate atomic row; no comma-separated lists of product IDs. Address is treated as one delivery label because this exercise does not query its internal components.
2NF: in an order-line representation keyed by (order_id,product_id), move order date/customer facts dependent only on order_id into orders; move current product facts dependent only on product_id into products.
3NF: move customer contact facts to customers and category names to categories. Non-key attributes depend on keys, not other non-key attributes, under the stated functional dependencies. Keep sale-time price on the line because it depends on the order-product pair.

The decomposition uses PK/FK links to reconstruct order details without repeating customer/category facts. Unique candidate keys enforce identity. No functional dependency is assumed from product_id alone to historical unit_price_kobo.

## Enforcement boundary
schema.sql enforces keys, referential integrity, permitted statuses, positive quantities and nonnegative stock/prices. The checkout transaction enforces stock availability and a matching database payment/line amount for the demonstrated purchase. The schema alone does NOT enforce payment sum equals order-line sum, legal status transitions or existence of a line for every committed order. These would need application services/triggers and further tests in production.

## Evidence
- er-diagram.png and er-diagram.mmd: cardinalities and entities.
- schema.sql: implemented DDL.
- data-profile.json: baseline synthetic row counts.
- constraint-tests.json: actual duplicate email, negative-stock, foreign-key and integrity tests.
Synthetic history is a reproducible reporting fixture, not a replay of inventory purchases; stock is independently seeded. Checkout alone tests inventory movement.
