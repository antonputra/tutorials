package main

import (
	"database/sql"
	"log"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

var actions = []string{"LOGIN", "SIGN UP", "LOGOUT", "SEARCH", "ADD TO CART", "CHECKOUT", "SUBSCRIBE", "DOWNLOAD", "UPLOAD", "CONTACT US"}

func main() {
	cfg := new(Config)
	cfg.loadConfig("config.yaml")

	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)
	StartPrometheusServer(cfg, reg)

	runTest(*cfg, m)
}

func runTest(cfg Config, m *metrics) {
	log.Printf("Running Test: %s-%s", cfg.Test.Db, cfg.Test.Op)
	currentClients := cfg.Test.MinClients

	db := dbConnect(cfg)
	stmt, err := prepStmt(db, cfg)
	if err != nil {
		log.Fatalf("Unable to prepare statement: %s", err)
	}

	for {
		clients := make(chan struct{}, currentClients)
		m.clients.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				runQuery(stmt, m, cfg)
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

func runQuery(stmt *sql.Stmt, m *metrics, cfg Config) {
	sleep(cfg.Test.RequestDelayMs)

	if cfg.Test.Op == "write" {
		e := Event{CustomerId: random(1, 11), Action: actions[random(0, 10)]}

		err := e.insert(stmt, m, cfg)
		if err != nil {
			log.Fatalf("Unable to insert data to db: %s", err)
		}
	} else {
		var c Customer

		err := c.read(stmt, m, random(1, cfg.Test.MaxEventId), cfg)
		if err != nil {
			log.Fatalf("Unable to read data to db: %s", err)
		}
	}
}
