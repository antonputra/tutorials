package main

import (
	"context"
	"flag"
	"fmt"
	"log/slog"
	"myapp/config"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/prometheus/client_golang/prometheus"

	"github.com/valyala/fasthttp"
)

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

	s := newServer(ctx, cfg, reg)
	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	fasthttp.ListenAndServe(appPort, s.handler)
}
