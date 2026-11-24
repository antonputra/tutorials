-- The payments table after a run: how many payments, for how many invoices, and the total.
SELECT count(*) AS payments, count(DISTINCT invoice_number) AS invoices, sum(amount_usd) AS total_usd FROM payments;
-- Every invoice that was paid more than once.
SELECT invoice_number, count(*) AS payments, sum(amount_usd) AS total_usd FROM payments
GROUP BY invoice_number HAVING count(*) > 1 ORDER BY invoice_number;
