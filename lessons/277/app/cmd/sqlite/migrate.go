package main

import (
	"app/config"
	"app/sqlite"
	"context"
	"database/sql"

	"github.com/antonputra/go-utils/util"
)

func migrate(ctx context.Context, db *sql.DB, cfg *config.Config) {
	// Define create table functions.
	createTables := []func(*sql.DB) *sql.Stmt{
		sqlite.CreateCustomerTable,
		sqlite.CreateProductTable,
		sqlite.CreateCartTable,
		sqlite.CreateCartItemTable,
		sqlite.CreateOrderTable,
		sqlite.CreateOrderItemTable,
	}

	// Create database tables.
	for _, createFn := range createTables {
		stmt := createFn(db)
		_, err := stmt.ExecContext(ctx)
		stmt.Close()
		util.Fail(err, "failed to create table")
	}

	// Define create index functions.
	createIndexes := []func(*sql.DB) *sql.Stmt{
		sqlite.CreateCartCustomerIndex,
		sqlite.CreateCartItemCartIndex,
		sqlite.CreateCartItemProductIndex,
		sqlite.CreateOrderCustomerIndex,
		sqlite.CreateOrderItemOrderIndex,
		sqlite.CreateOrderItemProductIndex,
	}

	// Create database indexes.
	for _, createFn := range createIndexes {
		stmt := createFn(db)
		_, err := stmt.ExecContext(ctx)
		stmt.Close()
		util.Fail(err, "failed to create index")
	}

	// Insert Customers.
	stmt := sqlite.InsertCustomer(db)
	defer stmt.Close()
	for _, customer := range cfg.Customers {
		err := customer.InsertCustomerSQL(ctx, stmt)
		util.Fail(err, "failed to insert customer")
	}

	// Insert Products.
	stmt = sqlite.InsertProduct(db)
	defer stmt.Close()
	for _, product := range cfg.Products {
		err := product.InsertProductSQL(ctx, stmt)
		util.Fail(err, "failed to insert product")
	}
}
