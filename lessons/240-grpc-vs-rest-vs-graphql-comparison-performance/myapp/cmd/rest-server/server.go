package main

import (
	"context"
	"myapp/config"
	"myapp/db"
	"net/http"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/jackc/pgx/v5/pgxpool"
	jsoniter "github.com/json-iterator/go"
	"github.com/prometheus/client_golang/prometheus"
)

// json - jsoniter object
var json = jsoniter.ConfigFastest

type server struct {
	db  *pgxpool.Pool
	cfg *config.Config
	m   *mon.Metrics
}

type resp struct {
	Msg string `json:"msg"`
}

func newServer(ctx context.Context, cfg *config.Config, reg *prometheus.Registry) *server {
	m := mon.NewMetrics(reg)
	s := server{cfg: cfg, m: m}
	s.db = db.DbConnect(ctx, cfg)

	return &s
}

func renderJSON(w http.ResponseWriter, value any, status int) {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := enc.Encode(value); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
