package main

import (
	"context"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

type Device struct {
	Id        int    `json:"id"`
	Uuid      string `json:"uuid"`
	Mac       string `json:"mac"`
	Firmware  string `json:"firmware"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

func (d *Device) save(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
		}
	}()

	// Execute the query to create a new device record (pgx automatically prepares and caches statements by default).
	sql := `INSERT INTO "go_device" (uuid, mac, firmware, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id`

	err = db.QueryRow(ctx, sql, d.Uuid, d.Mac, d.Firmware, d.CreatedAt, d.UpdatedAt).Scan(&d.Id)

	return util.Annotate(err, "db.Exec failed")
}
