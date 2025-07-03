package main

import (
	"context"
	"log/slog"
	"time"
)

func runTest(cfg *Config, db string, m *metrics) {
	slog.Info("Starting a test", "db", db)

	ctx, done := context.WithCancel(context.Background())
	defer done()

	var pg *postgres
	var mg *mongodb

	if db == "pg" {
		pg = NewPostgres(ctx, cfg)
	} else {
		mg = NewMongo(ctx, cfg)
	}

	sleepInterval := cfg.Test.RequestDelayMs

	currentClients := cfg.Test.MinClients

	for {
		clients := make(chan struct{}, currentClients)
		slog.Info("New", "clients", currentClients)

		m.clients.Set(float64(currentClients))
		now := time.Now()
		for {
			clients <- struct{}{}

			go func() {
				// Create Product 10 products
				var p product
				for range 9 {
					p = product{
						Name:        genString(20),
						Description: genString(100),
						Price:       float32(random(1, 100)),
						Stock:       100,
						Colors:      []string{genString(5), genString(5)},
					}
					warn(p.create(pg, mg, db, m), "create product failed")
				}

				p2 := product{
					Name:        genString(20),
					Description: genString(100),
					Price:       float32(random(1, 100)),
					Stock:       100,
					Colors:      []string{genString(5), genString(5)},
				}
				warn(p2.create(pg, mg, db, m), "create product failed")

				// Update stock quantity of the product
				p2.Stock = random(1, 100)
				warn(p2.update(pg, mg, db, m), "update product failed")

				// Search for products with low price
				warn(p.search(pg, mg, db, m, cfg.Debug), "search product failed")

				// Delete product
				warn(p.delete(pg, mg, db, m), "delete product failed")

				if sleepInterval > 0 {
					sleep(sleepInterval)
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
