package main

import (
	"flag"
	"log/slog"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	db := flag.String("db", "", "database to test")
	flag.Parse()
	util.ValidateStr(*db, []string{"redis", "redis-cluster", "dragonfly"})

	cfg := new(Config)
	cfg.loadConfig("config.yaml")

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	reg := prometheus.NewRegistry()
	m := mon.NewMetrics(reg)
	mon.StartPrometheusServer(cfg.MetricsPort, reg)

	runTest(*cfg, m, *db)
}
