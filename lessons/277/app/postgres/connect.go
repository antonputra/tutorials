// Package sqlite provides utilities to connect to the PostgreSQL database.
package postgres

import (
	"app/config"
	"context"
	"fmt"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

func Connect(ctx context.Context, cfg *config.Config) *pgxpool.Pool {
	uri := fmt.Sprintf("host=%s user=%s password=%s dbname=%s pool_max_conns=%d",
		cfg.Postgres.Host, cfg.Postgres.User, cfg.Postgres.Password, cfg.Postgres.Database, cfg.Postgres.MaxConnections)

	dbpool, err := pgxpool.New(ctx, uri)
	util.Fail(err, "failed to connect to postgres, host: %s", cfg.Postgres.Host)

	return dbpool
}
