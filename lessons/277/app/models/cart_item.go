package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type CartItem struct {
	Id        int64
	CartId    int64
	ProductId int64
	Quantity  int64
}

func (c *CartItem) InsertCartItemSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_cart_item").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, c.CartId, c.ProductId, c.Quantity).Scan(&c.Id)

	return util.Annotate(err, "InsertCartItem failed")
}

func (c *CartItem) DeleteCartItemSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("delete", "delete_cart_item").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, c.CartId).Scan(&c.Id)

	return util.Annotate(err, "DeleteCartItem failed")
}

func (c *CartItem) InsertCartItemPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_cart_item").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `INSERT INTO cart_item(cart_id, product_id, quantity) VALUES ($1, $2, $3) RETURNING id;`

	err = db.QueryRow(ctx, sql, c.CartId, c.ProductId, c.Quantity).Scan(&c.Id)

	return util.Annotate(err, "InsertCartItem failed")
}

func (c *CartItem) DeleteCartItemPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("delete", "delete_cart_item").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `DELETE FROM cart_item WHERE cart_id = $1 RETURNING id;`

	err = db.QueryRow(ctx, sql, c.CartId).Scan(&c.Id)

	return util.Annotate(err, "DeleteCartItem failed")
}
