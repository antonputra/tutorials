package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type OrderItem struct {
	Id        int64
	OrderId   int64
	ProductId int64
	Quantity  int64
}

func (o *OrderItem) InsertOrderItemSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_order_item").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, o.OrderId, o.ProductId, o.Quantity).Scan(&o.Id)

	return util.Annotate(err, "InsertOrderItem failed")
}

func (o *OrderItem) InsertOrderItemPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_order_item").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `INSERT INTO order_item(order_id, product_id, quantity) VALUES ($1, $2, $3) RETURNING id;`

	err = db.QueryRow(ctx, sql, o.OrderId, o.ProductId, o.Quantity).Scan(&o.Id)

	return util.Annotate(err, "InsertOrderItem failed")
}
