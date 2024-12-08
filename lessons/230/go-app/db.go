package main

import (
	"context"
	"fmt"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

func dbConnect(ctx context.Context, cfg *Config) *pgxpool.Pool {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s?pool_max_conns=%d",
		cfg.DbConfig.User, cfg.DbConfig.Password, cfg.DbConfig.Host, cfg.DbConfig.Database, cfg.DbConfig.MaxConnections)

	dbpool, err := pgxpool.New(ctx, url)
	util.Fail(err, "failed to create connection pool")

	return dbpool
}
