package main

import (
	"flag"
	"fmt"
	"log"
	"log/slog"
	"net/http"
)

func main() {
	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	cfg := new(Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	s := newServer(cfg)

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/devices", s.getDevices)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Printf("Starting the web server on port %d", cfg.AppPort)
	log.Fatal(http.ListenAndServe(appPort, mux))
}
