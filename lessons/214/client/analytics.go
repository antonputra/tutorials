package main

import (
	"database/sql"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

type Event struct {
	Id         int
	CustomerId int
	Action     string
}

type Customer struct {
	Name    string
	Address string
	Action  string
}

func (e *Event) insert(stmt *sql.Stmt, m *metrics, cfg Config) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"db": cfg.Test.Db, "op": cfg.Test.Op}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(e.CustomerId, e.Action)
	return annotate(err, "stmt.Exec failed")
}

func (c *Customer) read(stmt *sql.Stmt, m *metrics, event_id int, cfg Config) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"db": cfg.Test.Db, "op": cfg.Test.Op}).Observe(time.Since(now).Seconds())
		}
	}()

	err = stmt.QueryRow(event_id).Scan(&c.Name, &c.Address, &c.Action)
	return annotate(err, "stmt.Exec failed")
}
