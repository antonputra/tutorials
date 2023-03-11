package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"

	pb "github.com/antonputra/tutorials/lessons/151/go-app/device"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/metric/instrument"
	"go.opentelemetry.io/otel/metric/instrument/syncfloat64"
	"go.opentelemetry.io/otel/sdk/metric"
	"google.golang.org/grpc"
)

var dv pb.Device

func init() {
	dv = pb.Device{Uuid: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}
}

func main() {
	exporter, err := prometheus.New()
	if err != nil {
		log.Fatal(err)
	}

	provider := metric.NewMeterProvider(metric.WithReader(exporter))
	meter := provider.Meter("lesson151")

	go serveMetrics()

	counter, err := meter.SyncFloat64().Counter("myapp_http_requests", instrument.WithDescription("Number of HTTP requests."))
	if err != nil {
		log.Fatal(err)
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", 8082))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	ctx := context.Background()
	s := grpc.NewServer()
	server := &server{
		ctx:     ctx,
		counter: counter,
	}
	pb.RegisterManagerServer(s, server)
	s.Serve(lis)
}

type server struct {
	ctx     context.Context
	counter syncfloat64.Counter
	pb.UnimplementedManagerServer
}

func (s *server) GetEnvoyDevice(context.Context, *pb.DeviceRequest) (*pb.Device, error) {
	s.counter.Add(s.ctx, 1, []attribute.KeyValue{attribute.Key("proxy").String("envoy")}...)
	return &dv, nil
}

func (s *server) GetNginxDevice(context.Context, *pb.DeviceRequest) (*pb.Device, error) {
	s.counter.Add(s.ctx, 1, []attribute.KeyValue{attribute.Key("proxy").String("nginx")}...)
	return &dv, nil
}

func serveMetrics() {
	http.Handle("/metrics", promhttp.Handler())
	err := http.ListenAndServe(":9092", nil)
	if err != nil {
		log.Fatal(err)
		return
	}
}
