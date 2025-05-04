package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"
	"myapp/config"
	"net/http"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	ctx, done := context.WithCancel(context.Background())
	defer done()

	cfg := new(config.Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	reg := prometheus.NewRegistry()
	mon.StartPrometheusServer(cfg.MetricsPort, reg)

	s := newServer(ctx, cfg, reg)

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/devices", s.getDevices)
	mux.HandleFunc("POST /api/devices", s.saveDevice)
	mux.HandleFunc("GET /healthz", s.getHealth)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Printf("Starting the web server on port %d", cfg.AppPort)
	log.Fatal(http.ListenAndServe(appPort, mux))
}
