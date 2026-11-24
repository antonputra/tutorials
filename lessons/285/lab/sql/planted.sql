-- Every invoice line that differs from its purchase order line, or is not on the purchase order at all.
SELECT il.invoice_number, s.name AS supplier, i.po_number, il.sku, il.quantity AS billed, pl.quantity AS ordered,
       il.unit_price AS billed_price, pl.unit_price AS po_price,
       il.quantity * il.unit_price - coalesce(pl.quantity * pl.unit_price, 0) AS difference_usd
FROM invoice_lines il JOIN invoices i USING (invoice_number) JOIN suppliers s USING (supplier_id)
LEFT JOIN po_lines pl ON pl.po_number = i.po_number AND pl.sku = il.sku
WHERE i.po_number IS NOT NULL AND (pl.sku IS NULL OR pl.quantity <> il.quantity OR pl.unit_price <> il.unit_price)
ORDER BY il.invoice_number, il.line_no;
-- Invoices that name no purchase order.
SELECT i.invoice_number, s.name AS supplier, i.total_usd FROM invoices i JOIN suppliers s USING (supplier_id)
WHERE i.po_number IS NULL;
-- Purchase orders billed by more than one invoice.
SELECT po_number, array_agg(invoice_number ORDER BY invoice_number) AS invoices, min(total_usd) AS total_usd
FROM invoices WHERE po_number IS NOT NULL GROUP BY po_number HAVING count(*) > 1;
-- The rest: lines that equal their purchase order line in product, quantity and price, out of all lines.
SELECT count(*) FILTER (WHERE pl.sku IS NOT NULL) AS lines_that_match, count(*) AS all_lines
FROM invoice_lines il JOIN invoices i USING (invoice_number)
LEFT JOIN po_lines pl ON pl.po_number = i.po_number AND pl.sku = il.sku AND pl.quantity = il.quantity
     AND pl.unit_price = il.unit_price;
