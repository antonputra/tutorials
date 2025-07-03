package main

import (
	"context"
	"log/slog"
	"myapp/config"
	"myapp/db"
	"myapp/device"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/gofiber/fiber/v3"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

type server struct {
	db  *pgxpool.Pool
	cfg *config.Config
	m   *mon.Metrics
}

func newServer(ctx context.Context, cfg *config.Config, reg *prometheus.Registry) *server {
	m := mon.NewMetrics(reg)
	s := server{cfg: cfg, m: m}
	s.db = db.DbConnect(ctx, cfg)

	return &s
}

func (s *server) getHealth(c fiber.Ctx) error {
	return c.SendStatus(200)
}

func (s *server) getDevices(c fiber.Ctx) error {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "44-39-34-5E-9C-F2", Firmware: "3.0.1"},
		{Id: 2, Mac: "2B-6E-79-C7-22-1B", Firmware: "1.8.9"},
		{Id: 3, Mac: "06-0A-79-47-18-E1", Firmware: "4.0.9"},
		{Id: 4, Mac: "68-32-8F-00-B6-F4", Firmware: "5.0.0"},
	}

	return c.Status(fiber.StatusOK).JSON(devices)
}

func (s *server) saveDevice(c fiber.Ctx) error {
	d := new(device.Device)

	if err := c.Bind().Body(d); err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		return util.Annotate(err, "failed to decode device")
	}

	sql := `INSERT INTO "fiber_device" (mac, firmware) VALUES ($1, $2) RETURNING id`
	err := d.Save(c.Context(), s.db, s.m, sql)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device")
		return util.Annotate(err, "failed to save device")
	}
	slog.Debug("device saved", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	return c.Status(fiber.StatusCreated).JSON(d)
}
