package main

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

// Device represents hardware device
type Device struct {

	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

// Save inserts a Device into the Postgres database.
func (d *Device) Save(ctx context.Context, db *pgxpool.Pool, m *metrics) (err error) {
	// Get the current time to record the duration of the request.
	now := time.Now()
	defer func() {
		if err == nil {
			// Record the duration of the insert query.
			m.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())
		}
	}()

	// Execute the query to create a new image record (pgx automatically prepares and caches statements by default).
	_, err = db.Exec(ctx, `INSERT INTO "go_device" (id, mac, firmware) VALUES ($1, $2, $3)`, d.UUID, d.Mac, d.Firmware)
	return annotate(err, "db.Exec failed")
}
