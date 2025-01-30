package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"log/slog"
	"myapp/config"
	"myapp/db"
	"myapp/device"
	"net"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"google.golang.org/grpc"
)

func main() {
	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	ctx, done := context.WithCancel(context.Background())
	defer done()

	cfg := new(config.Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	reg := prometheus.NewRegistry()
	mon.StartPrometheusServer(cfg.MetricsPort, reg)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	lis, err := net.Listen("tcp", appPort)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	ns := newServer(ctx, cfg, reg)

	device.RegisterCloudServer(s, ns)
	s.Serve(lis)
}

type server struct {
	db  *pgxpool.Pool
	cfg *config.Config
	m   *mon.Metrics
	device.UnimplementedCloudServer
}

func newServer(ctx context.Context, cfg *config.Config, reg *prometheus.Registry) *server {
	m := mon.NewMetrics(reg)
	r := server{cfg: cfg, m: m}
	r.db = db.DbConnect(ctx, cfg)

	return &r
}

func (s *server) GetDevices(context.Context, *device.DeviceRequest) (*device.DeviceResponse, error) {
	ds := []*device.Device{
		{
			Id:        1,
			Uuid:      "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
			Mac:       "EF-2B-C4-F5-D6-34",
			Firmware:  "2.1.5",
			CreatedAt: "2024-05-28T15:21:51.137Z",
			UpdatedAt: "2024-05-28T15:21:51.137Z",
		},
		{
			Id:        2,
			Uuid:      "d2293412-36eb-46e7-9231-af7e9249fffe",
			Mac:       "E7-34-96-33-0C-4C",
			Firmware:  "1.0.3",
			CreatedAt: "2024-01-28T15:20:51.137Z",
			UpdatedAt: "2024-01-28T15:20:51.137Z",
		},
		{
			Id:        3,
			Uuid:      "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
			Mac:       "68-93-9B-B5-33-B9",
			Firmware:  "4.3.1",
			CreatedAt: "2024-08-28T15:18:21.137Z",
			UpdatedAt: "2024-08-28T15:18:21.137Z",
		},
	}

	dr := device.DeviceResponse{
		Devices: ds,
	}

	return &dr, nil
}

func (s *server) CreateDevice(ctx context.Context, dvr *device.CreateDeviceRequest) (*device.Device, error) {
	now := time.Now().Format(time.RFC3339Nano)

	d := &device.Device{
		Uuid:      uuid.New().String(),
		Mac:       dvr.Mac,
		Firmware:  dvr.Firmware,
		CreatedAt: now,
		UpdatedAt: now,
	}

	err := d.Insert(ctx, s.db, s.m)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device in postgres")
		return nil, err
	}
	slog.Debug("device saved in postgres", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	return d, nil
}
