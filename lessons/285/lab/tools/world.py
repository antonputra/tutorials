"""Compare the two databases the way no single agent can: what was ordered (juniper) and what arrived (receiving).

    python -m tools.world
"""
import os

import psycopg
from psycopg.rows import dict_row

with psycopg.connect(os.environ["JUNIPER_DB_URL"], row_factory=dict_row) as db:
    ordered = {(r["po_number"], r["sku"]): r for r in db.execute(
        "SELECT po_number, sku, description, quantity FROM po_lines").fetchall()}
    billed = {(r["po_number"], r["sku"]): r for r in db.execute(
        "SELECT i.po_number, il.sku, i.invoice_number, il.quantity FROM invoice_lines il JOIN invoices i"
        " USING (invoice_number) WHERE i.po_number IS NOT NULL AND il.sku <> 'FREIGHT'"
        " ORDER BY i.invoice_number DESC").fetchall()}
with psycopg.connect(os.environ["RECEIVING_DB_URL"], row_factory=dict_row) as db:
    received = {(r["po_number"], r["sku"]): r["quantity_received"] for r in db.execute(
        "SELECT r.po_number, l.sku, l.quantity_received FROM receipts r JOIN receipt_lines l USING (receipt_id)").fetchall()}

print(f"purchase order lines: {len(ordered)}, receipt lines: {len(received)}")
same = 0
for key, line in sorted(ordered.items()):
    got = received.get(key)
    if got == line["quantity"]:
        same += 1
    else:
        invoice = billed.get(key, {})
        print(f"{key[0]} {key[1]} {line['description']}: ordered {line['quantity']}, arrived {got}, "
              f"invoice {invoice.get('invoice_number')} bills {invoice.get('quantity')}")
print(f"lines where the quantity that arrived equals the quantity ordered: {same}")
for key in (("PO-2207", "CP-101"),):
    print(f"{key[0]} {key[1]}: ordered {ordered[key]['quantity']}, arrived {received[key]}, "
          f"invoice {billed[key]['invoice_number']} bills {billed[key]['quantity']}")
