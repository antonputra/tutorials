package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"time"

	pb "github.com/antonputra/tutorials/lessons/152/app/proto"
	"github.com/aristanetworks/goarista/monotime"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

var (
	serverAddr = flag.String("addr", "localhost:8082", "The server address in the format of host:port")
	sleep      = flag.String("sleep", "no", "Sleep for a second between retries.")
)

// Prometheus metrics for the application.
type metrics struct {
	// The duration of the producer sending the
	// message and the consumer receiving the message.
	duration *prometheus.SummaryVec
}

// NewMetrics constructs prometheus metrics.
func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		duration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "app",
			Name:       "request_duration_seconds",
			Help:       "Request duration.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"type"}),
	}
	reg.MustRegister(m.duration)
	return m
}

func main() {
	// Get command line arguments.
	flag.Parse()
	// Create a new Prometheus registry.
	reg := prometheus.NewRegistry()
	// Initialize the metrics with the new registry.
	m := NewMetrics(reg)

	// Create a new ServeMux for the Prometheus handler.
	pMux := http.NewServeMux()
	// Create a Prometheus handler with only a defined registry.
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	// Expose Prometheus metrics at /metrics endpoint.
	pMux.Handle("/metrics", promHandler)

	// Run the Prometheus HTTP server in the goroutine.
	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	// Define connection options.
	var opts []grpc.DialOption
	// Connect to gRPC server using h2c protocol (Plaintext - HTTP2 over TCP).
	opts = append(opts, grpc.WithTransportCredentials(insecure.NewCredentials()))

	// Connect to the gRPC server.
	conn, err := grpc.Dial(*serverAddr, opts...)
	if err != nil {
		log.Fatalf("grpc.Dial failed: %v", err)
	}
	defer conn.Close()

	// Define the time interval to resend the message.
	interval := 100 * time.Millisecond
	// Create a client to send requests to the server.
	client := pb.NewManagerClient(conn)
	for {
		// Create new UUID for each new message.
		id := uuid.New().String()
		// Create a timestamp for each new message.
		t := monotime.Now()
		// Create protobuf message to send to the kafka.
		msg := pb.Message{Uuid: id, Created: t}

		// Send a request to the gRPC server.
		message, err := client.GetMessage(context.Background(), &msg)
		if err != nil {
			log.Fatalf("client.GetMessage failed: %v", err)
		}

		// Record the time it took to send and receive the message.
		m.duration.With(prometheus.Labels{"type": "grpc"}).Observe(float64(monotime.Since(message.Created).Seconds()))
		// Sleep for the given interval before repeating.
		if *sleep == "yes" {
			time.Sleep(interval)
		}
	}
}
