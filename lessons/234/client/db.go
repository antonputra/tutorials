package main

import (
	"context"
	"fmt"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

func dbConnect(ctx context.Context, cfg *Config) *pgxpool.Pool {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s?pool_max_conns=%d",
		cfg.Db.User, cfg.Db.Password, cfg.Db.Host, cfg.Db.Database, cfg.Db.MaxConnections)

	dbpool, err := pgxpool.New(ctx, url)
	util.Fail(err, "failed to create connection pool")

	return dbpool
}
