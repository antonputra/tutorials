package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"

	"myapp/config"
	"myapp/db"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/panjf2000/gnet/v2"
	"github.com/prometheus/client_golang/prometheus"
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
	m := mon.NewMetrics(reg)

	hs := &httpServer{
		addr:      fmt.Sprintf("tcp://0.0.0.0:%d", cfg.AppPort),
		multicore: true,
		cfg:       cfg,
		m:         m,
		db:        db.DbConnect(ctx, cfg),
	}
	log.Println("server exits:", gnet.Run(hs, hs.addr, gnet.WithMulticore(true)))
}
