# Python vs JavaScript Performance: Best Backend Language 2026 (FastAPI vs Bun)

You can find tutorial [here](https://youtu.be/hQGE_CAo1PE).

## Schema

```sql
CREATE TABLE customer (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50),
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  address VARCHAR(255)
);

CREATE TABLE product (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  price DECIMAL(10,2),
  stock_quantity INTEGER
);

CREATE TABLE cart (
  id SERIAL PRIMARY KEY,
  customer_id BIGINT REFERENCES customer(id),
  total DECIMAL(10,2)
);

CREATE TABLE cart_item (
  id SERIAL PRIMARY KEY,
  cart_id BIGINT REFERENCES cart(id),
  product_id BIGINT REFERENCES product(id),
  quantity INTEGER
);

CREATE TABLE "order" (
  id SERIAL PRIMARY KEY,
  customer_id BIGINT REFERENCES customer(id),
  total DECIMAL(10,2)
);

CREATE TABLE order_item (
  id SERIAL PRIMARY KEY,
  order_id BIGINT REFERENCES "order"(id),
  product_id BIGINT REFERENCES product(id),
  quantity INTEGER
);

-- Create index on all foreign key columns for faster query performance.
CREATE INDEX cart_customer_id_idx ON cart (customer_id);
CREATE INDEX cart_item_cart_id_idx ON cart_item (cart_id);
CREATE INDEX cart_item_product_id_idx ON cart_item (product_id);
CREATE INDEX order_customer_id_idx ON "order" (customer_id);
CREATE INDEX order_item_order_id_idx ON order_item (order_id);
CREATE INDEX order_item_product_id_idx ON order_item (product_id);

-- Insert customers
INSERT INTO customer(username, first_name, last_name, address)
VALUES
  ('vmartin', 'Victor', 'Martin', '994 Lowndes Hill Park Road'),
  ('chauk', 'Christopher', 'Hauk', '4505 Cunningham Court'),
  ('hyoung', 'Howard', 'Young', '2001 Fairfax Drive'),
  ('jballard', 'John', 'Ballard', '1034 Ethels Lane'),
  ('jevans', 'James', 'Evans', '4669 Keyser Ridge Road'),
  ('egonzalez', 'Edgar', 'Gonzalez', '841 Marietta Street'),
  ('rbrumbelow', 'Ronald', 'Brumbelow', '4168 Rhapsody Street'),
  ('rharris', 'Raphael', 'Harris', '26 Red Bud Lane'),
  ('tfanning', 'Terry', 'Fanning', '2864 Bungalow Road'),
  ('ckelley', 'Claude', 'Kelley', '4896 Jarvisville Road');

-- Insert products
INSERT INTO product(name, price, stock_quantity)
VALUES
  ('Shampoo', 7.90, 100),
  ('Hairspray', 12.30, 100),
  ('Nail clippers', 19.00, 100),
  ('Towels', 32.80, 100),
  ('Conditioner', 8.80, 100),
  ('Detangler', 12.90, 100),
  ('Body wash ', 10.10, 100),
  ('Toilet paper ', 6.70, 100),
  ('Plunger', 23.90, 100),
  ('Mousse', 13.50, 100);
```

## Test

```sql
-- Create shopping cart
INSERT INTO cart(customer_id, total) VALUES (4, 0);

-- Add body wash to the cart
INSERT INTO cart_item(cart_id, product_id, quantity) VALUES (1, 7, 1);

-- Update value of the cart
UPDATE cart SET total = 10.10 WHERE customer_id = 4;

-- Create an order
INSERT INTO "order"(customer_id, total) VALUES (4, 25.90);

-- Add body wash to the order
INSERT INTO order_item(order_id, product_id, quantity) VALUES (1, 7, 1);

-- Reduce the stock quantity of the body wash
UPDATE product SET stock_quantity = 99 WHERE id = 7;

-- Delete shopping cart and items
DELETE FROM cart_item WHERE cart_id = 1;
DELETE FROM cart WHERE id = 1;

-- Select the order
SELECT 
    oi.id AS order_item_id,
    p.name AS product_name,
    oi.quantity,
    p.price,
    (oi.quantity * p.price) AS total_item_price
FROM order_item oi
JOIN product p ON oi.product_id = p.id
WHERE oi.order_id = 1;
```
