-- Invoice 1042, its lines, and the purchase order it names.
SELECT i.invoice_number, s.name AS supplier, i.po_number, i.invoice_date, i.due_date, i.total_usd, i.status
FROM invoices i JOIN suppliers s USING (supplier_id) WHERE i.invoice_number = 1042;
SELECT line_no, sku, description, quantity, unit, unit_price, quantity * unit_price AS amount
FROM invoice_lines WHERE invoice_number = 1042 ORDER BY line_no;
SELECT p.po_number, p.order_date, p.status, l.line_no, l.sku, l.description, l.quantity, l.unit_price
FROM purchase_orders p JOIN po_lines l USING (po_number) WHERE p.po_number = 'PO-2207' ORDER BY l.line_no;
