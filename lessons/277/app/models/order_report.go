package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type OrderReport struct {
	OrderId         int64
	ProductName     string
	ProductQuantity int64
	ProductPrice    float64
	OrderTotal      float64
}

func (o *OrderReport) SelectOrderSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("select", "select_order").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, o.OrderId).Scan(&o.OrderId, &o.ProductName, &o.ProductQuantity, &o.ProductPrice, &o.OrderTotal)

	return util.Annotate(err, "SelectOrder failed")
}

func (o *OrderReport) SelectOrderPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("select", "select_order").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `
    SELECT 
        oi.id AS order_item_id,
        p.name AS product_name,
        oi.quantity,
        p.price,
        (oi.quantity * p.price) AS total_item_price
    FROM order_item oi
    JOIN product p ON oi.product_id = p.id
    WHERE oi.order_id = $1;`

	err = db.QueryRow(ctx, sql, o.OrderId).Scan(&o.OrderId, &o.ProductName, &o.ProductQuantity, &o.ProductPrice, &o.OrderTotal)

	return util.Annotate(err, "SelectOrder failed")
}
