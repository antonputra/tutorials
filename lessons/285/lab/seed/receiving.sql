-- The warehouse's own data: what really arrived. Only the receiving agent reads it.
CREATE TABLE receipts (
    receipt_id    integer PRIMARY KEY,
    po_number     text NOT NULL,
    received_date date NOT NULL,
    dock          text NOT NULL,
    received_by   text NOT NULL
);
CREATE TABLE receipt_lines (
    receipt_id        integer NOT NULL REFERENCES receipts,
    line_no           integer NOT NULL,
    sku               text NOT NULL,
    description       text NOT NULL,
    quantity_received integer NOT NULL,
    unit              text NOT NULL,
    PRIMARY KEY (receipt_id, line_no)
);
