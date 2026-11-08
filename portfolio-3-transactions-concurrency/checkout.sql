-- Execute with foreign_keys enabled. Application MUST check changes()=1 after UPDATE,
-- otherwise ROLLBACK. Values below are illustrative; Python test executes this workflow.
BEGIN IMMEDIATE;
UPDATE products SET stock=stock-1 WHERE product_id=1 AND stock>=1;
-- If changes()!=1: ROLLBACK and stop, do not execute remaining statements.
INSERT INTO orders VALUES(100001,1,'2026-11-08','paid');
INSERT INTO order_items SELECT 100001,product_id,1,price_kobo FROM products WHERE product_id=1;
INSERT INTO payments SELECT 100001,100001,'CHECKOUT-100001',price_kobo,'captured' FROM products WHERE product_id=1;
COMMIT;
-- This represents a database payment record, NOT an external payment-provider charge.
