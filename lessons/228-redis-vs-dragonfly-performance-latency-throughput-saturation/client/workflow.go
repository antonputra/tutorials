package main

import (
	"context"
	"log/slog"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/redis/go-redis/v9"
)

func runTest(cfg Config, m *mon.Metrics, db string) {
	slog.Info("running test", "db", db, "test", cfg.Test.Name)

	var ctx = context.Background()
	currentClients := cfg.Test.MinClients

	var rdb *redis.Client
	var crdb *redis.ClusterClient

	if db == "redis" {
		rdb = redis.NewClient(&redis.Options{
			Addr:     cfg.Redis.Addr,
			Password: "",
			DB:       0,
			PoolSize: 500,
		})
	} else if db == "dragonfly" {
		rdb = redis.NewClient(&redis.Options{
			Addr:     cfg.Dragonfly.Addr,
			Password: "",
			DB:       0,
			PoolSize: 500,
		})
	} else {
		crdb = redis.NewClusterClient(&redis.ClusterOptions{
			Addrs:    cfg.Redis.Addrs,
			Password: "",
			PoolSize: 500,
		})
	}

	for {
		clients := make(chan struct{}, currentClients)
		m.Clients.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				util.Sleep(cfg.Test.RequestDelayMs)

				u := NewUser()

				if db == "redis" || db == "dragonfly" {
					err := u.set(ctx, rdb, m, cfg.Redis.Expiration)
					util.Warn(err, "u.SaveToRedis failed")

					err = u.get(ctx, rdb, m)
					util.Warn(err, "u.GetFromRedis failed")
				} else {
					err := u.cset(ctx, crdb, m, cfg.Redis.Expiration)
					util.Warn(err, "u.SaveToRedis failed")

					err = u.cget(ctx, crdb, m)
					util.Warn(err, "u.GetFromRedis failed")
				}

				<-clients
			}()

			if time.Since(now).Seconds() >= float64(cfg.Test.StageIntervalS) {
				break
			}
		}

		if currentClients == cfg.Test.MaxClients {
			break
		}
		currentClients += 1
	}
}
