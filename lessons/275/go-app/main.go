package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"

	"github.com/gofiber/fiber/v3"
)

func main() {
	ctx, done := context.WithCancel(context.Background())
	defer done()

	cp := flag.String("config", "config.yaml", "path to the config")
	flag.Parse()

	cfg := new(Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	app := fiber.New()
	s := newServer(ctx, cfg)

	app.Get("/api/users", s.getUsers)
	app.Post("/api/users", s.saveUser)
	app.Get("/healthz", s.getHealth)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Fatal(app.Listen(appPort))
}
