\set i random(1, 10000000)
SELECT customer_id AS c FROM orders WHERE id = :i \gset
SELECT id, created_at, status, total FROM orders WHERE customer_id = :c ORDER BY created_at DESC LIMIT 20;
