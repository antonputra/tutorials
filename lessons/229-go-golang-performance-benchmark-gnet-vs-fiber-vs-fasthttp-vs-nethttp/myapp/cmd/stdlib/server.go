package main

import (
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"myapp/config"
	"myapp/db"
	"myapp/device"
	"net/http"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

type server struct {
	db  *pgxpool.Pool
	cfg *config.Config
	m   *mon.Metrics
}

type resp struct {
	Msg string `json:"message"`
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

func (s *server) getHealth(w http.ResponseWriter, req *http.Request) {
	io.WriteString(w, "OK")
}

func (s *server) getDevices(w http.ResponseWriter, req *http.Request) {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "44-39-34-5E-9C-F2", Firmware: "3.0.1"},
		{Id: 2, Mac: "2B-6E-79-C7-22-1B", Firmware: "1.8.9"},
		{Id: 3, Mac: "06-0A-79-47-18-E1", Firmware: "4.0.9"},
		{Id: 4, Mac: "68-32-8F-00-B6-F4", Firmware: "5.0.0"},
	}

	renderJSON(w, &devices, 200)
}

func (s *server) saveDevice(w http.ResponseWriter, req *http.Request) {
	ctx := req.Context()

	decoder := json.NewDecoder(req.Body)
	d := new(device.Device)
	err := decoder.Decode(&d)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		renderJSON(w, resp{Msg: "failed to decode device"}, 400)
		return
	}

	sql := `INSERT INTO "stdlib_device" (mac, firmware) VALUES ($1, $2) RETURNING id`
	err = d.Save(ctx, s.db, s.m, sql)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device")
		renderJSON(w, resp{Msg: "failed to save device"}, 400)
		return
	}
	slog.Debug("device saved", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	renderJSON(w, &d, 201)
}
