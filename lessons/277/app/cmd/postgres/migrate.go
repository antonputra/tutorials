package main

import (
	"app/config"
	"context"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

func migrate(ctx context.Context, db *pgxpool.Pool, cfg *config.Config) {
	// PostgreSQL driver automatically prepares and caches statements.
	tables := []string{
		`
		CREATE TABLE IF NOT EXISTS customer (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50),
			first_name VARCHAR(50),
			last_name VARCHAR(50),
			address VARCHAR(255)
		);
		`,
		`
		CREATE TABLE IF NOT EXISTS product (
			id SERIAL PRIMARY KEY,
			name VARCHAR(100),
			price DECIMAL(10,2),
			stock_quantity INTEGER
		);
		`,
		`
		CREATE TABLE IF NOT EXISTS cart (
			id SERIAL PRIMARY KEY,
			customer_id BIGINT REFERENCES customer(id),
			total DECIMAL(10,2)
		);
		`,
		`
		CREATE TABLE IF NOT EXISTS cart_item (
			id SERIAL PRIMARY KEY,
			cart_id BIGINT REFERENCES cart(id),
			product_id BIGINT REFERENCES product(id),
			quantity INTEGER
		);
		`,
		`
		CREATE TABLE IF NOT EXISTS "order" (
			id SERIAL PRIMARY KEY,
			customer_id BIGINT REFERENCES customer(id),
			total DECIMAL(10,2)
		);
		`,
		`
		CREATE TABLE IF NOT EXISTS order_item (
			id SERIAL PRIMARY KEY,
			order_id BIGINT REFERENCES "order"(id),
			product_id BIGINT REFERENCES product(id),
			quantity INTEGER
		);
		`,
	}

	indexes := []string{
		`CREATE INDEX IF NOT EXISTS cart_customer_id_idx ON cart (customer_id);`,
		`CREATE INDEX IF NOT EXISTS cart_item_cart_id_idx ON cart_item (cart_id);`,
		`CREATE INDEX IF NOT EXISTS cart_item_product_id_idx ON cart_item (product_id);`,
		`CREATE INDEX IF NOT EXISTS order_customer_id_idx ON "order" (customer_id);`,
		`CREATE INDEX IF NOT EXISTS order_item_order_id_idx ON order_item (order_id);`,
		`CREATE INDEX IF NOT EXISTS order_item_product_id_idx ON order_item (product_id);`,
	}

	for _, sql := range tables {
		_, err := db.Exec(ctx, sql)
		util.Fail(err, "failed to create tables")
	}

	for _, sql := range indexes {
		_, err := db.Exec(ctx, sql)
		util.Fail(err, "failed to create indexes")
	}

	for _, c := range cfg.Customers {
		err := c.InsertCustomerPGX(ctx, db)
		util.Fail(err, "failed to create customer")
	}

	for _, p := range cfg.Products {
		err := p.InsertProductPGX(ctx, db)
		util.Fail(err, "failed to create product")
	}
}
