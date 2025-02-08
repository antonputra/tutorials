package main

import (
	"flag"
	"fmt"
	"log"
	"log/slog"
)

func main() {
	cp := flag.String("config", "config.yaml", "path to the config")
	flag.Parse()

	cfg := new(Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	s := newServer(cfg)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Fatal(s.serve(appPort))
}
