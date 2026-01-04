package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Order struct {
	Id         int64
	CustomerId int64
	Total      float64
}

func (o *Order) InsertOrderSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_order").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, o.CustomerId, o.Total).Scan(&o.Id)

	return util.Annotate(err, "InsertOrder failed")
}

func (o *Order) InsertOrderPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("insert", "insert_order").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `INSERT INTO "order"(customer_id, total) VALUES ($1, $2) RETURNING id;`

	err = db.QueryRow(ctx, sql, o.CustomerId, o.Total).Scan(&o.Id)

	return util.Annotate(err, "InsertOrder failed")
}
