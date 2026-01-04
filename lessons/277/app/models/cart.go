package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Cart struct {
	Id         int64
	CustomerId int64
	Total      float64
}

func (c *Cart) InsertCartSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_cart").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, c.CustomerId, c.Total).Scan(&c.Id)

	return util.Annotate(err, "InsertCart failed")
}

func (c *Cart) UpdateCartSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("update", "update_cart").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, c.Total, c.CustomerId).Scan(&c.Id)

	return util.Annotate(err, "UpdateCart failed")
}

func (c *Cart) DeleteCartSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("delete", "delete_cart").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, c.Id).Scan(&c.Id)

	return util.Annotate(err, "DeleteCart failed")
}

func (c *Cart) InsertCartPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_cart").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `INSERT INTO cart(customer_id, total) VALUES ($1, $2) RETURNING id;`

	err = db.QueryRow(ctx, sql, c.CustomerId, c.Total).Scan(&c.Id)

	return util.Annotate(err, "InsertCart failed")
}

func (c *Cart) UpdateCartPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("update", "update_cart").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `UPDATE cart SET total = $1 WHERE customer_id = $2 RETURNING id;`

	err = db.QueryRow(ctx, sql, c.Total, c.CustomerId).Scan(&c.Id)

	return util.Annotate(err, "UpdateCart failed")
}

func (c *Cart) DeleteCartPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("delete", "delete_cart").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `DELETE FROM cart WHERE id = $1 RETURNING id;`

	err = db.QueryRow(ctx, sql, c.Id).Scan(&c.Id)

	return util.Annotate(err, "DeleteCart failed")
}
