package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/gofiber/fiber/v3"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// handler to connect to S3 and Database
type handler struct {

	// Prometheus metrics
	metrics *metrics

	// S3 seesion, should be shared
	sess *session.Session

	// Postgres connection pool
	dbpool *pgxpool.Pool

	// App configuration object
	config *Config
}

var counter int = 0

func main() {
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

	// Initialize Fiber handler.
	h := handler{config: &c, metrics: m}
	h.s3Connect()
	h.dbConnect()

	app := fiber.New()

	app.Get("/healthz", h.getHealth)
	app.Get("/api/devices", h.getDevices)
	app.Get("/api/images", h.getImage)

	appPort := fmt.Sprintf(":%d", c.AppPort)
	log.Fatal(app.Listen(appPort))
}

// getHealth returns the status of the application.
func (h *handler) getHealth(c fiber.Ctx) error {
	// Placeholder for the health check
	return c.SendStatus(200)
}

// getDevices returns a list of connected devices.
func (h *handler) getDevices(c fiber.Ctx) error {
	devices := []Device{
		{UUID: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{UUID: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
		{UUID: "b16d0b53-14f1-4c11-8e29-b9fcef167c26", Mac: "62-46-13-B7-B3-A1", Firmware: "3.0.0"},
		{UUID: "51bb1937-e005-4327-a3bd-9f32dcf00db8", Mac: "96-A8-DE-5B-77-14", Firmware: "1.0.1"},
		{UUID: "e0a1d085-dce5-48db-a794-35640113fa67", Mac: "7E-3B-62-A6-09-12", Firmware: "3.5.6"},
	}

	return c.Status(http.StatusOK).JSON(devices)
}

// getImage downloads image from S3
func (h *handler) getImage(c fiber.Ctx) error {
	imgKey := fmt.Sprintf("go-thumbnail-%d.png", counter)

	// Generate a new image.
	image := NewImage(imgKey)

	// Upload the image to S3.
	err := upload(h.sess, h.config.S3Config.Bucket, imgKey, h.config.S3Config.ImagePath, h.metrics)
	if err != nil {
		log.Printf("upload failed: %v", err)
		return c.Status(http.StatusInternalServerError).SendString("internal error")
	}

	// Save the image metadata to db.
	err = save(image, "go_image", h.dbpool, h.metrics)
	if err != nil {
		log.Printf("save failed: %v", err)
		return c.Status(http.StatusInternalServerError).SendString("internal error")
	}
	counter += 1

	return c.Status(http.StatusOK).SendString("Saved!")
}

// s3Connect initializes the S3 session.
func (h *handler) s3Connect() {
	// Get credentials to authorize with AWS S3 API.
	crds := credentials.NewStaticCredentials(h.config.S3Config.User, h.config.S3Config.Secret, "")

	// Create S3 config.
	s3c := aws.Config{
		Region:           &h.config.S3Config.Region,
		Endpoint:         &h.config.S3Config.Endpoint,
		S3ForcePathStyle: &h.config.S3Config.PathStyle,
		Credentials:      crds,
	}

	// Establish a new session with the AWS S3 API.
	h.sess = session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
		Config:            s3c,
	}))
}

// dbConnect creates a connection pool to connect to Postgres.
func (h *handler) dbConnect() {
	url := fmt.Sprintf("postgres://%s:%s@%s:5432/%s",
		h.config.DbConfig.User, h.config.DbConfig.Password, h.config.DbConfig.Host, h.config.DbConfig.Database)

	// Connect to the Postgres database.
	dbpool, err := pgxpool.New(context.Background(), url)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %s", err)
	}

	h.dbpool = dbpool
}
