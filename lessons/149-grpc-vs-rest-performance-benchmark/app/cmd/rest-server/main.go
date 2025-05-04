package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	pb "github.com/antonputra/tutorials/lessons/149/app/event"
	"github.com/antonputra/tutorials/lessons/149/app/serializer"
	"github.com/gofiber/fiber/v2"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var ev pb.Event

type metrics struct {
	serialDuration *prometheus.SummaryVec
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		serialDuration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "app",
			Name:       "serial_duration_seconds",
			Help:       "Duration of the serialization.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"action", "type"}),
	}
	reg.MustRegister(m.serialDuration)
	return m
}

func init() {
	ev = pb.Event{
		Version:        "2.0",
		RouteKey:       "ANY /bot",
		RawPath:        "/default/bot",
		RawQueryString: "",
		Headers: &pb.Headers{
			Accept:                 "*/*",
			AcceptEncoding:         "gzip,deflate",
			ContentLength:          "129",
			ContentType:            "application/json",
			Host:                   "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
			UserAgent:              "Slackbot 1.0 (+https://api.slack.com/robots)",
			XAmznTraceId:           "Root=1-60f9f121-0e6b301236f5d57d46fbd0e1",
			XForwardedFor:          "3.94.92.68",
			XForwardedPort:         "443",
			XForwardedProto:        "https",
			XSlackRequestTimestamp: "1626992929",
			XSlackSignature:        "v0=d12f7cb55add77074248241c2ec2d3c9fe4611e7879a965c92315edd8f0ec0cf",
		},
		RequestContext: &pb.RequestContext{
			AccountId:    "424432388155",
			ApiId:        "4o68t2fwke",
			DomainName:   "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
			DomainPrefix: "4o68t2fwke",
			Http: &pb.Http{
				Method:    "POST",
				Path:      "/default/bot",
				Protocol:  "HTTP/1.1",
				SourcePp:  "3.94.92.68",
				UserAgent: "Slackbot 1.0 (+https://api.slack.com/robots)",
			},
			RequestId: "C5KdVjAlIAMEPzg=",
			RouteKey:  "ANY /bot",
			Stage:     "default",
			Time:      "22/Jul/2021:22:28:49 +0000",
			TimeEpoch: 1626992929961,
		},
		Body:            "{\"token\":\"UdG3UFNsPGoobvRzK5F2oIqe\",\"challenge\":\"6KaNtlamllYYaLZ7qhHxZbzyYut62TlDKu2wAZXp4rZlInRbcDTH\",\"type\":\"url_verification\"}",
		IsBase64Encoded: false,
	}
}

func main() {
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	tj := testJSON(m)
	tp := testProtoBuf(m)

	app := fiber.New()

	app.Get("/api/events/:id", getEvent)
	app.Get("/api/test-json", tj)
	app.Get("/api/test-protobuf", tp)

	// Create Prometheus HTTP server to expose metrics
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	log.Fatalln(app.Listen(":8080"))
}

func getEvent(c *fiber.Ctx) error {
	b, err := json.Marshal(&ev)
	if err != nil {
		return err
	}
	c.Set("content-type", "application/json")
	return c.Send(b)
}

func testJSON(m *metrics) func(*fiber.Ctx) error {
	return func(c *fiber.Ctx) error {
		// serialize go struct to json string
		now := time.Now()
		b, err := serializer.SerializeJSON(&ev)
		if err != nil {
			return err
		}
		m.serialDuration.With(prometheus.Labels{"action": "serialize", "type": "json"}).Observe(time.Since(now).Seconds())

		// deserialize json string to go struct
		now = time.Now()
		_, err = serializer.DeserializeJSON(b)
		if err != nil {
			return err
		}
		m.serialDuration.With(prometheus.Labels{"action": "deserialize", "type": "json"}).Observe(time.Since(now).Seconds())

		return err
	}
}

func testProtoBuf(m *metrics) func(*fiber.Ctx) error {
	return func(c *fiber.Ctx) error {
		// serialize go struct to protobuf
		now := time.Now()
		b, err := serializer.SerializeProtoBuf(&ev)
		if err != nil {
			return err
		}
		m.serialDuration.With(prometheus.Labels{"action": "serialize", "type": "protobuf"}).Observe(time.Since(now).Seconds())

		// deserialize protobuf to go struct
		now = time.Now()
		_, err = serializer.DeserializeProtoBuf(b)
		if err != nil {
			return err
		}
		m.serialDuration.With(prometheus.Labels{"action": "deserialize", "type": "protobuf"}).Observe(time.Since(now).Seconds())

		return err
	}
}
