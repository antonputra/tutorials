package device

import (
	"context"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Device struct {
	Id       int    `json:"id"`
	Mac      string `json:"mac"`
	Firmware string `json:"firmware"`
}

func (d *Device) Save(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics, sql string) (err error) {
	err = db.QueryRow(ctx, sql, d.Mac, d.Firmware).Scan(&d.Id)
	return util.Annotate(err, "db.Exec failed")
}
