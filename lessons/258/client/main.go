package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/antonputra/go-utils/util"
	"github.com/redis/go-redis/v9"

	"github.com/prometheus/client_golang/prometheus"
)

var host string

func init() {
	host = os.Getenv("REDIS_HOST")
	if host == "" {
		log.Fatalln("You MUST set REDIS_HOST env variable!")
	}
}

func main() {
	cfg := new(Config)
	cfg.loadConfig("config.yaml")

	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)
	StartPrometheusServer(cfg, reg)

	runTest(*cfg, m)
}

func runTest(cfg Config, m *metrics) {

	var ctx = context.Background()
	currentClients := cfg.Test.MinClients

	rdb := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:6379", host),
		Password: "",
		DB:       0,
	})

	for {
		clients := make(chan struct{}, currentClients)
		m.stage.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				util.Sleep(cfg.Test.RequestDelayMs)

				u := NewUser()

				err := u.SaveToRedis(ctx, rdb, m, cfg.Redis.Expiration, cfg.Debug)
				util.Warn(err, "u.SaveToRedis failed")

				err = u.GetFromRedis(ctx, rdb, m, cfg.Debug)
				util.Warn(err, "u.GetFromRedis failed")

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
