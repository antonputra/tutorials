-- What a payment run did to the business data, and whether anything was done twice.
SELECT (SELECT count(*) FROM payments) AS payment_rows, (SELECT count(DISTINCT invoice_number) FROM payments) AS invoices_paid,
       (SELECT sum(amount_usd) FROM payments) AS paid_usd,
       (SELECT count(*) FROM holds) AS hold_rows, (SELECT count(DISTINCT invoice_number) FROM holds) AS invoices_held;
-- Invoices with more than one payment row.
SELECT invoice_number, count(*) AS payment_rows, array_agg(payment_id ORDER BY payment_id) AS payment_ids,
       sum(amount_usd) AS scheduled_usd FROM payments GROUP BY invoice_number HAVING count(*) > 1;
-- Tool calls that reached the database more than once with the same arguments.
SELECT action, args->>'invoice_number' AS invoice, args->>'po_number' AS po, count(*) AS times,
       count(DISTINCT process) AS processes FROM access_log GROUP BY 1, 2, 3 HAVING count(*) > 1 ORDER BY 2, 1;
-- Which process ran how many tool calls, and when.
SELECT process, count(*) AS tool_calls, to_char(min(at), 'HH24:MI:SS.MS') AS first_call,
       to_char(max(at), 'HH24:MI:SS.MS') AS last_call FROM access_log GROUP BY process ORDER BY min(at);
-- The holds.
SELECT invoice_number, reason FROM holds ORDER BY hold_id;
