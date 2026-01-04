package models

import (
	"context"
	"database/sql"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Product struct {
	Id            int64   `yaml:"id"`
	Name          string  `yaml:"name"`
	Price         float64 `yaml:"price"`
	StockQuantity int64   `yaml:"stock_quantity"`
}

func (p *Product) InsertProductSQL(ctx context.Context, stmt *sql.Stmt) (err error) {
	err = stmt.QueryRowContext(ctx, p.Id, p.Name, p.Price, p.StockQuantity).Scan(&p.Id)

	return util.Annotate(err, "InsertProduct failed")
}

func (p *Product) UpdateProductSQL(ctx context.Context, stmt *sql.Stmt, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("update", "update_product").Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRowContext(ctx, p.StockQuantity, p.Id).Scan(&p.Id)

	return util.Annotate(err, "UpdateProduct failed")
}

func (p *Product) InsertProductPGX(ctx context.Context, db *pgxpool.Pool) (err error) {
	// PostgreSQL driver automatically prepares and caches statements.
	sql := `
	INSERT INTO product(id, name, price, stock_quantity)
	VALUES ($1, $2, $3, $4) RETURNING id;`

	err = db.QueryRow(ctx, sql, p.Id, p.Name, p.Price, p.StockQuantity).Scan(&p.Id)

	return util.Annotate(err, "InsertProduct failed")
}

func (p *Product) UpdateProductPGX(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Hist.WithLabelValues("update", "update_product").Observe(time.Since(now).Seconds())
		}
	}()

	sql := `UPDATE product SET stock_quantity = $1 WHERE id = $2 RETURNING id;`

	err = db.QueryRow(ctx, sql, p.StockQuantity, p.Id).Scan(&p.Id)

	return util.Annotate(err, "UpdateProduct failed")
}
