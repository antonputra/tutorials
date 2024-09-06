package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

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
func NewMyServer() *MyServer {

	// Load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

	// Create Prometheus registry
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	// Create Prometheus HTTP server to expose metrics
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	// Start an HTTP server to expose Prometheus metrics in the background.
	metricsPort := fmt.Sprintf(":%d", c.MetricsPort)
	go func() {
		log.Fatal(http.ListenAndServe(metricsPort, pMux))
	}()

	ms := MyServer{
		config:  &c,
		metrics: m,
	}

	ms.s3Connect()
	ms.dbConnect()

	return &ms
}

func renderJSON(w http.ResponseWriter, s interface{}) {
	b, err := json.Marshal(s)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(b)
}

func main() {

	// Initialize MyServer.
	ms := NewMyServer()

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/devices", ms.getDevices)
	mux.HandleFunc("GET /api/images", ms.getImage)
	mux.HandleFunc("GET /healthz", ms.getHealth)

	appPort := fmt.Sprintf(":%d", ms.config.AppPort)
	log.Fatal(http.ListenAndServe(appPort, mux))
}

// getHealth returns the status of the application.
func (ms *MyServer) getHealth(w http.ResponseWriter, req *http.Request) {
	// Placeholder for the health check
	w.Write([]byte("OK"))
}

// getDevices returns a list of connected devices.
func (ms *MyServer) getDevices(w http.ResponseWriter, req *http.Request) {
	devices := []Device{
		{UUID: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{UUID: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
		{UUID: "b16d0b53-14f1-4c11-8e29-b9fcef167c26", Mac: "62-46-13-B7-B3-A1", Firmware: "3.0.0"},
		{UUID: "51bb1937-e005-4327-a3bd-9f32dcf00db8", Mac: "96-A8-DE-5B-77-14", Firmware: "1.0.1"},
		{UUID: "e0a1d085-dce5-48db-a794-35640113fa67", Mac: "7E-3B-62-A6-09-12", Firmware: "3.5.6"},
	}

	renderJSON(w, devices)
}

// getImage downloads image from S3
func (ms *MyServer) getImage(w http.ResponseWriter, req *http.Request) {

	// Generate a new image.
	image := NewImage()

	// Upload the image to S3.
	err := upload(ms.s3, ms.config.S3Config.Bucket, image.Key, ms.config.S3Config.ImagePath, ms.metrics)
	if err != nil {
		log.Printf("upload failed: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("internal error"))

	}

	// Save the image metadata to db.
	err = image.save(ms.db, ms.metrics)
	if err != nil {
		log.Printf("save failed: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("internal error"))
	}

	w.Write([]byte("Saved!"))
}

// s3Connect initializes the S3 session.
func (ms *MyServer) s3Connect() {

	// Load the credentials and initialize the S3 configuration.
	s3c, err := config.LoadDefaultConfig(context.TODO())
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
func (ms *MyServer) dbConnect() {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s",
		ms.config.DbConfig.User, ms.config.DbConfig.Password, ms.config.DbConfig.Host, ms.config.DbConfig.Database)

	// Connect to the Postgres database.
	dbpool, err := pgxpool.New(context.Background(), url)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %s", err)
	}

	ms.db = dbpool
}
