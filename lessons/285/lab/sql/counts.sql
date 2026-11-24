-- How many rows each table of the business database holds.
SELECT 'suppliers' AS table_name, count(*) FROM suppliers
UNION ALL SELECT 'purchase_orders', count(*) FROM purchase_orders
UNION ALL SELECT 'po_lines', count(*) FROM po_lines
UNION ALL SELECT 'invoices', count(*) FROM invoices
UNION ALL SELECT 'invoice_lines', count(*) FROM invoice_lines
UNION ALL SELECT 'payments', count(*) FROM payments
UNION ALL SELECT 'holds', count(*) FROM holds
UNION ALL SELECT 'access_log', count(*) FROM access_log;
-- The invoices of the Friday run.
SELECT count(*) AS invoices, min(invoice_number) AS first, max(invoice_number) AS last, min(due_date) AS due,
       count(DISTINCT supplier_id) AS suppliers, sum(total_usd) AS total_usd,
       sum(length(document_text)) AS characters_of_paper
FROM invoices;
SELECT min(n) AS fewest_lines, max(n) AS most_lines FROM (SELECT count(*) AS n FROM invoice_lines GROUP BY invoice_number) t;
