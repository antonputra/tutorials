-- Juniper Market's own business data. The agent reads it and writes to it only through its tools.
CREATE TABLE suppliers (
    supplier_id   integer PRIMARY KEY,
    name          text NOT NULL UNIQUE,
    street        text NOT NULL,
    city          text NOT NULL,
    state         text NOT NULL,
    zip           text NOT NULL,
    phone         text NOT NULL,
    email         text NOT NULL,
    terms_days    integer NOT NULL
);
CREATE TABLE purchase_orders (
    po_number     text PRIMARY KEY,
    supplier_id   integer NOT NULL REFERENCES suppliers,
    order_date    date NOT NULL,
    status        text NOT NULL
);
CREATE TABLE po_lines (
    po_number     text NOT NULL REFERENCES purchase_orders,
    line_no       integer NOT NULL,
    sku           text NOT NULL,
    description   text NOT NULL,
    quantity      integer NOT NULL,
    unit          text NOT NULL,
    unit_price    numeric(10,2) NOT NULL,
    PRIMARY KEY (po_number, line_no)
);
CREATE TABLE invoices (
    invoice_number integer PRIMARY KEY,
    supplier_id    integer NOT NULL REFERENCES suppliers,
    po_number      text REFERENCES purchase_orders,
    invoice_date   date NOT NULL,
    due_date       date NOT NULL,
    total_usd      numeric(10,2) NOT NULL,
    status         text NOT NULL DEFAULT 'open',
    document_text  text NOT NULL
);
CREATE TABLE invoice_lines (
    invoice_number integer NOT NULL REFERENCES invoices,
    line_no        integer NOT NULL,
    sku            text NOT NULL,
    description    text NOT NULL,
    quantity       integer NOT NULL,
    unit           text NOT NULL,
    unit_price     numeric(10,2) NOT NULL,
    PRIMARY KEY (invoice_number, line_no)
);
-- The risky table: a row here is money that goes out on the pay date.
-- idempotency_key is NULL unless the tool is told to use one (PAYMENTS_IDEMPOTENT=1).
CREATE TABLE payments (
    payment_id      bigserial PRIMARY KEY,
    invoice_number  integer NOT NULL REFERENCES invoices,
    amount_usd      numeric(10,2) NOT NULL,
    note            text NOT NULL,
    pay_date        date NOT NULL,
    scheduled_at    timestamptz NOT NULL DEFAULT now(),
    scheduled_by    text NOT NULL,
    idempotency_key text UNIQUE
);
CREATE TABLE holds (
    hold_id        bigserial PRIMARY KEY,
    invoice_number integer NOT NULL REFERENCES invoices,
    reason         text NOT NULL,
    held_at        timestamptz NOT NULL DEFAULT now(),
    held_by        text NOT NULL
);
-- Every tool call that reaches the business data leaves a row: who, what, and from which process.
CREATE TABLE access_log (
    id      bigserial PRIMARY KEY,
    at      timestamptz NOT NULL DEFAULT now(),
    actor   text NOT NULL,
    process text NOT NULL,
    action  text NOT NULL,
    args    jsonb NOT NULL
);
