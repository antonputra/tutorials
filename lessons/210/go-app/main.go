package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// MyServer used to connect to S3 and Database.
type MyServer struct {

	// Postgres connection pool.
	db *pgxpool.Pool

	// Application configuration object.
	config *Config

	// Prometheus metrics.
	metrics *metrics
}

type Response struct {
	Message string `json:"message"`
}

// Initializes MyServer and establishes connections with S3 and the database.
func NewMyServer(ctx context.Context, c *Config, reg *prometheus.Registry) *MyServer {
	// Create Prometheus metrics.
	m := NewMetrics(reg)

	ms := MyServer{
		config:  c,
		metrics: m,
	}
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
		log.Printf("Starting the Prometheus server on port %d", c.MetricsPort)
		log.Fatal(http.ListenAndServe(metricsPort, pMux))
	}()
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

func main() {
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
	mux.HandleFunc("POST /api/devices", ms.saveDevice)
	mux.HandleFunc("GET /healthz", ms.getHealth)

	appPort := fmt.Sprintf(":%d", cfg.AppPort)
	log.Printf("Starting the web server on port %d", cfg.AppPort)
	log.Fatal(http.ListenAndServe(appPort, mux))
}

// getHealth returns the status of the application.
func (ms *MyServer) getHealth(w http.ResponseWriter, req *http.Request) {
	// Placeholder for the health check
	io.WriteString(w, "OK")
}

// getDevices returns a list of connected devices.
func (ms *MyServer) getDevices(w http.ResponseWriter, req *http.Request) {
	device := Device{UUID: "9add349c-c35c-4d32-ab0f-53da1ba40a2d", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}

	renderJSON(w, &device, 200)
}

// saveDevice registers the device.
func (ms *MyServer) saveDevice(w http.ResponseWriter, req *http.Request) {
	ctx := req.Context()

	// Parse the device from the request.
	decoder := json.NewDecoder(req.Body)
	var d Device
	err := decoder.Decode(&d)
	if err != nil {
		log.Printf("decoder.Decode failed: %s", err)
		renderJSON(w, Response{Message: "Failed to decode Device."}, 400)
		return
	}

	// Generate a new UUID for the device.
	d.UUID = uuid.New().String()

	// Save the device to the database.
	err = d.Save(ctx, ms.db, ms.metrics)
	if err != nil {
		log.Printf("d.Save failed: %s", err)
		renderJSON(w, Response{Message: "Failed to save Device."}, 400)
		return
	}

	renderJSON(w, &d, 201)
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

// annotate adds a context message to an error while wrapping it. The context
// message will be formatted with fmt.Sprintf. If there is no error, then none
// of the arguments are processed, and nil is returned for ease of use.
func annotate(err error, format string, args ...any) error {
	if err != nil {
		return fmt.Errorf("%s: %w", fmt.Sprintf(format, args...), err)
	}
	return nil
}
