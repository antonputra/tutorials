"""The payables agent's tools, as plain Python functions. Each one returns a JSON string.

Nothing here knows about a model or an agent. The model never runs these: it asks, and our loop calls them.
The first three read Juniper Market's business database. The last two write to it.
"""
import json
import os
import socket
import time
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row

DB_URL = os.environ.get("JUNIPER_DB_URL", "postgresql://postgres@postgres:5432/juniper")
ACTOR = os.environ.get("ACTOR", "payables-agent")
PROCESS = f"{socket.gethostname()}:{os.getpid()}"     # which container and process ran the tool


def _db():
    return psycopg.connect(DB_URL, row_factory=dict_row)


def _json(value) -> str:
    return json.dumps(value, default=str)             # money and dates travel as text: "38.00", "2026-11-27"


def _log(db, action: str, **args) -> None:
    db.execute("INSERT INTO access_log (actor, process, action, args) VALUES (%s, %s, %s, %s)",
               (ACTOR, PROCESS, action, json.dumps(args)))


def list_invoices_due(due_date: str, include_documents: bool = False) -> str:
    """List the invoices due on a date (YYYY-MM-DD): number, supplier, purchase order number and total."""
    with _db() as db:
        _log(db, "list_invoices_due", due_date=due_date, include_documents=include_documents)
        rows = db.execute(
            "SELECT i.invoice_number, s.name AS supplier, i.po_number, i.total_usd, i.status"
            + (", i.document_text" if include_documents else "")
            + " FROM invoices i JOIN suppliers s USING (supplier_id) WHERE i.due_date = %s ORDER BY i.invoice_number",
            (due_date,)).fetchall()
    return _json({"due_date": due_date, "count": len(rows), "invoices": rows})


def get_invoice(invoice_number: int) -> str:
    """Get one supplier invoice: supplier, purchase order number, lines, total and the text of the paper invoice."""
    with _db() as db:
        _log(db, "get_invoice", invoice_number=invoice_number)
        inv = db.execute(
            "SELECT i.invoice_number, s.name AS supplier, i.po_number, i.invoice_date, i.due_date, i.total_usd,"
            " i.status, i.document_text FROM invoices i JOIN suppliers s USING (supplier_id)"
            " WHERE i.invoice_number = %s", (invoice_number,)).fetchone()
        if inv is None:
            return _json({"error": f"there is no invoice {invoice_number}"})
        lines = db.execute(
            "SELECT line_no, sku, description, quantity, unit, unit_price, quantity * unit_price AS amount"
            " FROM invoice_lines WHERE invoice_number = %s ORDER BY line_no", (invoice_number,)).fetchall()
    document = inv.pop("document_text")
    return _json({**inv, "lines": lines, "document_text": document})


def get_purchase_order(po_number: str) -> str:
    """Get one purchase order: what Juniper Market ordered, at what price, and the invoices billed against it."""
    with _db() as db:
        _log(db, "get_purchase_order", po_number=po_number)
        po = db.execute(
            "SELECT p.po_number, s.name AS supplier, p.order_date, p.status FROM purchase_orders p"
            " JOIN suppliers s USING (supplier_id) WHERE p.po_number = %s", (po_number,)).fetchone()
        if po is None:
            return _json({"error": f"there is no purchase order {po_number}"})
        lines = db.execute(
            "SELECT line_no, sku, description, quantity, unit, unit_price FROM po_lines"
            " WHERE po_number = %s ORDER BY line_no", (po_number,)).fetchall()
        invoices = db.execute(
            "SELECT invoice_number, total_usd, status FROM invoices WHERE po_number = %s ORDER BY invoice_number",
            (po_number,)).fetchall()
    return _json({**po, "lines": lines, "invoices": invoices})


def hold_invoice(invoice_number: int, reason: str) -> str:
    """Put an invoice on hold so it is not paid, and record the reason."""
    with _db() as db:
        _log(db, "hold_invoice", invoice_number=invoice_number, reason=reason)
        if db.execute("SELECT 1 FROM invoices WHERE invoice_number = %s", (invoice_number,)).fetchone() is None:
            return _json({"error": f"there is no invoice {invoice_number}"})
        hold = db.execute("INSERT INTO holds (invoice_number, reason, held_by) VALUES (%s, %s, %s) RETURNING hold_id",
                          (invoice_number, reason, ACTOR)).fetchone()
        db.execute("UPDATE invoices SET status = 'on_hold' WHERE invoice_number = %s", (invoice_number,))
    return _json({"invoice_number": invoice_number, "status": "on_hold", "hold_id": hold["hold_id"]})


def schedule_payment(invoice_number: int, amount_usd: float, note: str) -> str:
    """Schedule the payment of an invoice for its due date. This moves money: it writes a row in payments."""
    amount = Decimal(str(amount_usd)).quantize(Decimal("0.01"))
    # With PAYMENTS_IDEMPOTENT=1 the same invoice can be scheduled only once, however often this runs.
    key = f"invoice-{invoice_number}" if os.environ.get("PAYMENTS_IDEMPOTENT") == "1" else None
    with _db() as db:
        _log(db, "schedule_payment", invoice_number=invoice_number, amount_usd=str(amount), note=note)
        inv = db.execute("SELECT due_date FROM invoices WHERE invoice_number = %s", (invoice_number,)).fetchone()
        if inv is None:
            return _json({"error": f"there is no invoice {invoice_number}"})
        row = db.execute(
            "INSERT INTO payments (invoice_number, amount_usd, note, pay_date, scheduled_by, idempotency_key)"
            " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (idempotency_key) DO NOTHING"
            " RETURNING payment_id, invoice_number, amount_usd, pay_date",
            (invoice_number, amount, note, inv["due_date"], ACTOR, key)).fetchone()
        already = row is None
        if already:
            row = db.execute("SELECT payment_id, invoice_number, amount_usd, pay_date FROM payments"
                             " WHERE idempotency_key = %s", (key,)).fetchone()
        else:
            db.execute("UPDATE invoices SET status = 'scheduled' WHERE invoice_number = %s", (invoice_number,))
    # The row is committed. A real bank can take a while to confirm; the agent has not heard back yet.
    time.sleep(float(os.environ.get("PAYMENT_CONFIRM_SECONDS", "0")))
    return _json({**row, "status": "scheduled", **({"already_scheduled": True} if already else {})})


TOOLS = {f.__name__: f for f in (list_invoices_due, get_invoice, get_purchase_order, hold_invoice, schedule_payment)}
