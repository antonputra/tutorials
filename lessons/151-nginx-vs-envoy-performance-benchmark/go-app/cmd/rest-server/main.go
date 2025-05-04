package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	pb "github.com/antonputra/tutorials/lessons/151/go-app/device"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/valyala/fasthttp"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/metric/instrument"
	"go.opentelemetry.io/otel/sdk/metric"
)

var dvs []pb.Device

func init() {
	dvs = []pb.Device{
		{Uuid: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Uuid: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
	}
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

	hl := func(ctx *fasthttp.RequestCtx) {
		switch string(ctx.Path()) {
		case "/api-envoy/devices":
			devices(ctx)
			counter.Add(ctx, 1, []attribute.KeyValue{attribute.Key("proxy").String("envoy")}...)
		case "/api-nginx/devices":
			devices(ctx)
			counter.Add(ctx, 1, []attribute.KeyValue{attribute.Key("proxy").String("nginx")}...)
		default:
			res := fmt.Sprintf("%s path is not supported", ctx.Path())
			ctx.Error(res, fasthttp.StatusNotFound)
		}
	}

	fasthttp.ListenAndServe(":8080", hl)
}

func devices(ctx *fasthttp.RequestCtx) {
	b, err := json.Marshal(dvs)
	if err != nil {
		ctx.Error("json.Marshal failed", fasthttp.StatusInternalServerError)
		return
	}
	ctx.SetBody(b)
	ctx.SetStatusCode(fasthttp.StatusOK)
}

func serveMetrics() {
	http.Handle("/metrics", promhttp.Handler())
	err := http.ListenAndServe(":9091", nil)
	if err != nil {
		log.Fatal(err)
		return
	}
}
