package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"
	"myapp/config"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/gofiber/fiber/v3"
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

	app := fiber.New()
	s := newServer(ctx, cfg, reg)

	app.Get("/api/devices", s.getDevices)
	app.Post("/api/devices", s.saveDevice)
	app.Get("/healthz", s.getHealth)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Fatal(app.Listen(appPort))
}
