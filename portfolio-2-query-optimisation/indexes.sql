CREATE INDEX idx_orders_customer_date ON orders(customer_id,ordered_at DESC);
CREATE INDEX idx_items_product ON order_items(product_id);
ANALYZE;
