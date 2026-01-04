package sqlite

import (
	"database/sql"

	"github.com/antonputra/go-utils/util"
)

// CreateCustomerTable prepares a statement to create the customer table if it doesn't exist.
func CreateCustomerTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50),
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        address VARCHAR(255)
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCustomerTable")

	return stmt
}

// CreateProductTable prepares a statement to create the product table if it doesn't exist.
func CreateProductTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        price DECIMAL(10,2),
        stock_quantity INTEGER
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateProductTable")

	return stmt
}

// CreateCartTable prepares a statement to create the cart table if it doesn't exist.
func CreateCartTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY,
        customer_id BIGINT REFERENCES customer(id),
        total DECIMAL(10,2)
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCartTable")

	return stmt
}

// CreateCartItemTable prepares a statement to create the cart_item table if it doesn't exist.
func CreateCartItemTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS cart_item (
        id INTEGER PRIMARY KEY,
        cart_id BIGINT REFERENCES cart(id),
        product_id BIGINT REFERENCES product(id),
        quantity INTEGER
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCartItemTable")

	return stmt
}

// CreateOrderTable prepares a statement to create the order table if it doesn't exist.
func CreateOrderTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY,
        customer_id BIGINT REFERENCES customer(id),
        total DECIMAL(10,2)
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateOrderTable")

	return stmt
}

// CreateOrderItemTable prepares a statement to create the order_item table if it doesn't exist.
func CreateOrderItemTable(db *sql.DB) *sql.Stmt {
	sql := `
    CREATE TABLE IF NOT EXISTS order_item (
        id INTEGER PRIMARY KEY,
        order_id BIGINT REFERENCES "order"(id),
        product_id BIGINT REFERENCES product(id),
        quantity INTEGER
    );`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateOrderItemTable")

	return stmt
}

// CreateCartCustomerIndex prepares a statement to create an index on the customer_id in the cart table.
func CreateCartCustomerIndex(db *sql.DB) *sql.Stmt {
	sql := "CREATE INDEX IF NOT EXISTS cart_customer_id_idx ON cart (customer_id);"

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCartCustomerIndex")

	return stmt
}

// CreateCartItemCartIndex prepares a statement to create an index on the cart_id in the cart_item table.
func CreateCartItemCartIndex(db *sql.DB) *sql.Stmt {
	sql := "CREATE INDEX IF NOT EXISTS cart_item_cart_id_idx ON cart_item (cart_id);"

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCartItemCartIndex")

	return stmt
}

// CreateCartItemProductIndex prepares a statement to create an index on the product_id in the cart_item table.
func CreateCartItemProductIndex(db *sql.DB) *sql.Stmt {
	sql := "CREATE INDEX IF NOT EXISTS cart_item_product_id_idx ON cart_item (product_id);"

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateCartItemProductIndex")

	return stmt
}

// CreateOrderCustomerIndex prepares a statement to create an index on the customer_id in the order table.
func CreateOrderCustomerIndex(db *sql.DB) *sql.Stmt {
	sql := `CREATE INDEX IF NOT EXISTS order_customer_id_idx ON "order" (customer_id);`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateOrderCustomerIndex")

	return stmt
}

// CreateOrderItemOrderIndex prepares a statement to create an index on the order_id in the order_item table.
func CreateOrderItemOrderIndex(db *sql.DB) *sql.Stmt {
	sql := "CREATE INDEX IF NOT EXISTS order_item_order_id_idx ON order_item (order_id);"

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateOrderItemOrderIndex")

	return stmt
}

// CreateOrderItemProductIndex prepares a statement to create an index on the product_id in the order_item table.
func CreateOrderItemProductIndex(db *sql.DB) *sql.Stmt {
	sql := "CREATE INDEX IF NOT EXISTS order_item_product_id_idx ON order_item (product_id);"

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "CreateOrderItemProductIndex")

	return stmt
}

// InsertCustomer prepares a statement to insert a new customer and return the generated ID.
func InsertCustomer(db *sql.DB) *sql.Stmt {
	sql := `
    INSERT INTO customer(id, username, first_name, last_name, address)
    VALUES (?, ?, ?, ?, ?)
    RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertCustomer")

	return stmt
}

// InsertProduct prepares a statement to insert a new product and return the generated ID.
func InsertProduct(db *sql.DB) *sql.Stmt {
	sql := `
    INSERT INTO product(id, name, price, stock_quantity)
    VALUES (?, ?, ?, ?)
    RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertProduct")

	return stmt
}

// UpdateProduct prepares a statement to update a product's stock quantity.
func UpdateProduct(db *sql.DB) *sql.Stmt {
	sql := `UPDATE product SET stock_quantity = ? WHERE id = ? RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "UpdateProduct")

	return stmt
}

// InsertCart prepares a statement to create a new cart for a customer.
func InsertCart(db *sql.DB) *sql.Stmt {
	sql := `INSERT INTO cart(customer_id, total) VALUES (?, ?) RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertCart")

	return stmt
}

// UpdateCart prepares a statement to update the total value of a specific customer's cart.
func UpdateCart(db *sql.DB) *sql.Stmt {
	sql := `UPDATE cart SET total = ? WHERE customer_id = ? RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "UpdateCart")

	return stmt
}

// DeleteCart prepares a statement to remove a cart by its ID.
func DeleteCart(db *sql.DB) *sql.Stmt {
	sql := `DELETE FROM cart WHERE id = ? RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "DeleteCart")

	return stmt
}

// InsertCartItem prepares a statement to add a product to a cart.
func InsertCartItem(db *sql.DB) *sql.Stmt {
	sql := `INSERT INTO cart_item(cart_id, product_id, quantity) VALUES (?, ?, ?) RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertCartItem")

	return stmt
}

// DeleteCartItem prepares a statement to remove all items associated with a specific cart ID.
func DeleteCartItem(db *sql.DB) *sql.Stmt {
	sql := `DELETE FROM cart_item WHERE cart_id = ? RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "DeleteCartItem")

	return stmt
}

// InsertOrder prepares a statement to create a new order record.
func InsertOrder(db *sql.DB) *sql.Stmt {
	sql := `INSERT INTO "order"(customer_id, total) VALUES (?, ?) RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertOrder")

	return stmt
}

// InsertOrderItem prepares a statement to add a product record to a specific order.
func InsertOrderItem(db *sql.DB) *sql.Stmt {
	sql := `INSERT INTO order_item(order_id, product_id, quantity) VALUES (?, ?, ?) RETURNING id;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "InsertOrderItem")

	return stmt
}

// SelectOrder prepares a statement to retrieve order items with product details and calculated totals for a specific order.
func SelectOrder(db *sql.DB) *sql.Stmt {
	sql := `
    SELECT 
        oi.id AS order_item_id,
        p.name AS product_name,
        oi.quantity,
        p.price,
        (oi.quantity * p.price) AS total_item_price
    FROM order_item oi
    JOIN product p ON oi.product_id = p.id
    WHERE oi.order_id = ?;`

	stmt, err := db.Prepare(sql)
	util.Fail(err, "failed to prepare stmt=%s", "SelectOrder")

	return stmt
}
