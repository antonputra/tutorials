package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// MyServer used to connect to S3 and Database.
type MyServer struct {

	// S3 client, should be shared.
	s3 *s3.Client

	// Postgres connection pool.
	db *pgxpool.Pool

	// Application configuration object.
	config *Config

	// Prometheus metrics.
	metrics *metrics
}

// Initializes MyServer and establishes connections with S3 and the database.
func NewMyServer(ctx context.Context, c *Config, reg *prometheus.Registry) *MyServer {
	// Create Prometheus metrics.
	m := NewMetrics(reg)

	ms := MyServer{
		config:  c,
		metrics: m,
	}

	ms.s3Connect(ctx)
	ms.dbConnect(ctx)

	return &ms
}

func StartPrometheusServer(c *Config, reg *prometheus.Registry) {
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	// Start an HTTP server to expose Prometheus metrics in the background.
	metricsPort := fmt.Sprintf(":%d", c.MetricsPort)
	go func() {
		log.Fatal(http.ListenAndServe(metricsPort, pMux))
	}()
}

func renderJSON(w http.ResponseWriter, value any) {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)
	w.Header().Set("Content-Type", "application/json")
	if err := enc.Encode(value); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func main() {
	// [Improvement] Use context PR: https://github.com/antonputra/tutorials/pull/266
	ctx, done := context.WithCancel(context.Background())
	defer done()

	cfg := new(Config)
	cfg.loadConfig("config.yaml")

	reg := prometheus.NewRegistry()
	StartPrometheusServer(cfg, reg)

	// Initialize MyServer.
	ms := NewMyServer(ctx, cfg, reg)

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/devices", ms.getDevices)
	mux.HandleFunc("GET /api/images", ms.getImage)
	mux.HandleFunc("GET /healthz", ms.getHealth)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Fatal(http.ListenAndServe(appPort, mux))
}

// getHealth returns the status of the application.
func (ms *MyServer) getHealth(w http.ResponseWriter, req *http.Request) {
	// Placeholder for the health check
	io.WriteString(w, "OK")
}

// getDevices returns a list of connected devices.
func (ms *MyServer) getDevices(w http.ResponseWriter, req *http.Request) {
	device := Device{Id: 1, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}

	renderJSON(w, device)
}

// getImage downloads image from S3
func (ms *MyServer) getImage(w http.ResponseWriter, req *http.Request) {
	ctx := req.Context()

	// Generate a new image.
	image := NewImage()

	// To remain consistent with the Python implementation, measure the duration in this function.
	// Get the current time to record the duration of the request.
	now := time.Now()

	// Upload the image to S3.
	err := upload(ctx, ms.s3, ms.config.S3Config.Bucket, image.Key, ms.config.S3Config.ImagePath)
	if err != nil {
		log.Printf("upload failed: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		io.WriteString(w, "internal error")
	}

	// Record the duration of the request to S3.
	ms.metrics.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())

	// Get the current time to record the duration of the request.
	now = time.Now()

	// Save the image metadata to db.
	err = image.save(ctx, ms.db)
	if err != nil {
		log.Printf("save failed: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		io.WriteString(w, "internal error")
	}

	// Record the duration of the insert query.
	ms.metrics.duration.With(prometheus.Labels{"op": "s3"}).Observe(time.Since(now).Seconds())

	io.WriteString(w, "Saved!")
}

// s3Connect initializes the S3 session.
func (ms *MyServer) s3Connect(ctx context.Context) {

	// Load the credentials and initialize the S3 configuration.
	s3c, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		log.Fatalf("failed to load configuration, %v", err)
	}

	// Establish a new session with the AWS S3 API.
	ms.s3 = s3.NewFromConfig(s3c, func(o *s3.Options) {
		o.BaseEndpoint = &ms.config.S3Config.Endpoint
		o.UsePathStyle = ms.config.S3Config.PathStyle
		o.Region = ms.config.S3Config.Region
	})
}

// dbConnect creates a connection pool to connect to Postgres.
func (ms *MyServer) dbConnect(ctx context.Context) {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s?pool_max_conns=%d",
		ms.config.DbConfig.User, ms.config.DbConfig.Password, ms.config.DbConfig.Host, ms.config.DbConfig.Database, ms.config.DbConfig.MaxConnections)

	// Connect to the Postgres database.
	dbpool, err := pgxpool.New(ctx, url)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %s", err)
	}

	ms.db = dbpool
}
