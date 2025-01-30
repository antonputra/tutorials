package db

import (
	"context"
	"fmt"
	"myapp/config"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

func DbConnect(ctx context.Context, cfg *config.Config) *pgxpool.Pool {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s?pool_max_conns=%d",
		cfg.DatabaseConfig.User, cfg.DatabaseConfig.Password, cfg.DatabaseConfig.Host, cfg.DatabaseConfig.Database, cfg.DatabaseConfig.MaxConnections)

	dbpool, err := pgxpool.New(ctx, url)
	util.Fail(err, "failed to create connection pool")

	return dbpool
}
