-- Q1: customer order history; benchmark parameters: customer=42, cutoff=2026-04-01
SELECT order_id,ordered_at,status FROM orders WHERE customer_id=42 AND ordered_at>='2026-04-01' ORDER BY ordered_at DESC;
-- Q2: captured gross sales, not net revenue (refunds excluded)
SELECT substr(o.ordered_at,1,7) AS month,SUM(p.amount_kobo) AS captured_kobo FROM orders o JOIN payments p USING(order_id) WHERE p.status='captured' GROUP BY month ORDER BY month;
-- Q3: products with highest ordered quantities, excluding cancelled orders
SELECT p.product_id,p.name,SUM(i.quantity) AS units FROM order_items i JOIN products p USING(product_id) JOIN orders o USING(order_id) WHERE o.status<>'cancelled' GROUP BY p.product_id,p.name ORDER BY units DESC,p.product_id LIMIT 10;
-- Q4: customers without orders
SELECT c.customer_id,c.name FROM customers c WHERE NOT EXISTS(SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id);
-- Q5: customer ranking by captured payment amount
WITH spend AS (SELECT c.customer_id,c.name,COALESCE(SUM(CASE WHEN p.status='captured' THEN p.amount_kobo ELSE 0 END),0) AS kobo FROM customers c LEFT JOIN orders o USING(customer_id) LEFT JOIN payments p USING(order_id) GROUP BY c.customer_id,c.name) SELECT *,DENSE_RANK() OVER(ORDER BY kobo DESC) AS spending_rank FROM spend ORDER BY spending_rank,customer_id LIMIT 20;
-- Q6: stock alert
SELECT sku,name,stock FROM products WHERE stock<10 ORDER BY stock,sku;
