package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"myapp/config"
	"myapp/db"
	"myapp/device"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/valyala/fasthttp"
)

type server struct {
	db  *pgxpool.Pool
	cfg *config.Config
	m   *mon.Metrics
}

func (s *server) handler(ctx *fasthttp.RequestCtx) {
	switch string(ctx.Path()) {
	case "/healthz":
		s.getHealth((ctx))
	case "/api/devices":
		if string(ctx.Method()) == "GET" {
			s.getDevices((ctx))
		} else {
			s.saveDevice((ctx))
		}
	default:
		ctx.Error("not found", fasthttp.StatusNotFound)
	}
}

func (s *server) getHealth(ctx *fasthttp.RequestCtx) {
	ctx.SetStatusCode(fasthttp.StatusOK)
	fmt.Fprintf(ctx, "OK")
}

func (s *server) getDevices(ctx *fasthttp.RequestCtx) {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "44-39-34-5E-9C-F2", Firmware: "3.0.1"},
		{Id: 2, Mac: "2B-6E-79-C7-22-1B", Firmware: "1.8.9"},
		{Id: 3, Mac: "06-0A-79-47-18-E1", Firmware: "4.0.9"},
		{Id: 4, Mac: "68-32-8F-00-B6-F4", Firmware: "5.0.0"},
	}

	renderJSON(ctx, 200, devices)
}

func (s *server) saveDevice(ctx *fasthttp.RequestCtx) {
	d := new(device.Device)
	err := json.Unmarshal(ctx.Request.Body(), &d)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		ctx.Error("failed to decode device", 400)
		return
	}

	sql := `INSERT INTO "fasthttp_device" (mac, firmware) VALUES ($1, $2) RETURNING id`
	err = d.Save(ctx, s.db, s.m, sql)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device")
		ctx.Error("failed to save device", 400)
		return
	}
	slog.Debug("device saved", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	renderJSON(ctx, 201, d)
}

func renderJSON(ctx *fasthttp.RequestCtx, code int, value any) {
	enc := json.NewEncoder(ctx)
	enc.SetEscapeHTML(false)

	ctx.Response.Header.SetCanonical([]byte("Content-Type"), []byte("application/json"))
	ctx.Response.SetStatusCode(code)

	if err := enc.Encode(value); err != nil {
		ctx.Error(err.Error(), fasthttp.StatusInternalServerError)
	}
}

func newServer(ctx context.Context, cfg *config.Config, reg *prometheus.Registry) *server {
	m := mon.NewMetrics(reg)
	s := server{cfg: cfg, m: m}
	s.db = db.DbConnect(ctx, cfg)

	return &s
}
