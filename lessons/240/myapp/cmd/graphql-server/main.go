package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"
	"myapp/config"
	"myapp/graph"
	"net/http"

	"myapp/db"

	"github.com/99designs/gqlgen/graphql/handler"
	"github.com/99designs/gqlgen/graphql/handler/extension"
	"github.com/99designs/gqlgen/graphql/handler/lru"
	"github.com/99designs/gqlgen/graphql/handler/transport"
	"github.com/99designs/gqlgen/graphql/playground"
	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/vektah/gqlparser/v2/ast"
)

const defaultPort = "8080"

func main() {
	ctx, done := context.WithCancel(context.Background())
	defer done()

	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	cfg := new(config.Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	reg := prometheus.NewRegistry()
	mon.StartPrometheusServer(cfg.MetricsPort, reg)

	r := newServer(ctx, cfg, reg)

	srv := handler.New(graph.NewExecutableSchema(graph.Config{Resolvers: &r}))

	srv.AddTransport(transport.Options{})
	srv.AddTransport(transport.GET{})
	srv.AddTransport(transport.POST{})

	srv.SetQueryCache(lru.New[*ast.QueryDocument](1000))

	srv.Use(extension.Introspection{})
	srv.Use(extension.AutomaticPersistedQuery{
		Cache: lru.New[string](100),
	})

	http.Handle("/", playground.Handler("GraphQL playground", "/query"))
	http.Handle("/query", srv)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Fatal(http.ListenAndServe(appPort, nil))
}

func newServer(ctx context.Context, cfg *config.Config, reg *prometheus.Registry) graph.Resolver {
	m := mon.NewMetrics(reg)
	r := graph.Resolver{Cfg: cfg, M: m}
	r.Db = db.DbConnect(ctx, cfg)

	return r
}
