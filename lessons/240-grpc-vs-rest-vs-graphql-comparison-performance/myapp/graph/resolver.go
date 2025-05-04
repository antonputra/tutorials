package graph

//go:generate go run github.com/99designs/gqlgen generate

import (
	"myapp/config"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Resolver struct {
	Db  *pgxpool.Pool
	Cfg *config.Config
	M   *mon.Metrics
}
