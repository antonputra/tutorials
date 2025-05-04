package device

import (
	"context"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

type Device struct {
	Id       int    `json:"id"`
	Mac      string `json:"mac"`
	Firmware string `json:"firmware"`
}

func (d *Device) Save(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics, sql string) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
		}
	}()

	err = db.QueryRow(ctx, sql, d.Mac, d.Firmware).Scan(&d.Id)
	return util.Annotate(err, "db.Exec failed")
}
