package main

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

type postgres struct {
	// Postgres connection pool.
	dbpool *pgxpool.Pool

	// Application configuration object.
	config *Config

	// Context for the program
	context context.Context
}

// Initializes NewPostgres and establishes connections with database.
func NewPostgres(ctx context.Context, c *Config) *postgres {
	pg := postgres{
		config:  c,
		context: ctx,
	}
	pg.pgConnect(ctx)

	return &pg
}

// dbConnect creates a connection pool to connect to Postgres.
func (pg *postgres) pgConnect(ctx context.Context) {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s?pool_max_conns=%d",
		pg.config.Postgres.User, pg.config.Postgres.Password, pg.config.Postgres.Host, pg.config.Postgres.Database, pg.config.Postgres.MaxConnections)

	// Connect to the Postgres database.
	dbpool, err := pgxpool.New(ctx, url)
	fail(err, "Unable to create connection pool")

	pg.dbpool = dbpool
}
