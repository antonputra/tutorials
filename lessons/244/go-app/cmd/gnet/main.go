package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"

	"go-app/config"
	"go-app/db"

	"github.com/panjf2000/gnet/v2"
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

	hs := &httpServer{
		addr:      fmt.Sprintf("tcp://0.0.0.0:%d", cfg.AppPort),
		multicore: true,
		cfg:       cfg,
		db:        db.DbConnect(ctx, cfg),
	}
	log.Println("server exits:", gnet.Run(hs, hs.addr, gnet.WithMulticore(true)))
}
