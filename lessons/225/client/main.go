package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/redis/go-redis/v9"

	"github.com/bradfitz/gomemcache/memcache"
	"github.com/prometheus/client_golang/prometheus"
)

var client string

func init() {
	client = os.Getenv("CLIENT")
	if client == "" {
		log.Fatalln("You MUST set CLIENT env variable!")
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
	log.Printf("Running Test: %s-%s\n", client, cfg.Test.Name)

	var ctx = context.Background()
	currentClients := cfg.Test.MinClients

	var rdb *redis.Client
	var mc *memcache.Client

	if client == "memcache" {
		mc = memcache.New(fmt.Sprintf("%s:11211", cfg.Memcache.Host))
		mc.MaxIdleConns = 500
	} else {
		rdb = redis.NewClient(&redis.Options{
			Addr:     fmt.Sprintf("%s:6379", cfg.Redis.Host),
			Password: "",
			DB:       0,
			PoolSize: 500,
		})
	}

	for {
		clients := make(chan struct{}, currentClients)
		m.stage.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				sleep(cfg.Test.RequestDelayMs)

				u := NewUser()

				if client == "memcache" {
					err := u.SaveToMC(mc, m, cfg.Memcache.Expiration, cfg.Debug)
					warning(err, "u.SaveToMC failed")

					err = u.GetFromMC(mc, m, cfg.Debug)
					warning(err, "u.GetFromMC failed")
				} else {
					err := u.SaveToRedis(ctx, rdb, m, cfg.Redis.Expiration, cfg.Debug)
					warning(err, "u.SaveToRedis failed")

					err = u.GetFromRedis(ctx, rdb, m, cfg.Debug)
					warning(err, "u.GetFromRedis failed")
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
