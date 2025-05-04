package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/sdk/resource"
	oteltrace "go.opentelemetry.io/otel/sdk/trace"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
	"go.opentelemetry.io/otel/trace"
)

var (
	tracer trace.Tracer
)

// Console Exporter, only for testing
func newConsoleExporter() (oteltrace.SpanExporter, error) {
	return stdouttrace.New()
}

// OpenTelemetry Protocol Exporter (OTLP) Exporter
func newOTLPExporter(ctx context.Context, otlpEndpoint string) (oteltrace.SpanExporter, error) {
	// Change default HTTPS -> HTTP.
	insecureOpt := otlptracehttp.WithInsecure()

	// Update default OTLP reciver endpoint.
	endpointOpt := otlptracehttp.WithEndpoint(otlpEndpoint)

	return otlptracehttp.New(ctx, insecureOpt, endpointOpt)
}

// TracerProvider is an OpenTelemetry TracerProvider.
// It provides Tracers to instrumentation so it can trace operational flow through a system.
func newTraceProvider(exp sdktrace.SpanExporter) *sdktrace.TracerProvider {
	// Ensure default SDK resources and the required service name are set.
	r, err := resource.Merge(resource.Default(), resource.NewWithAttributes(
		semconv.SchemaURL,
		semconv.ServiceName("go-app"),
	))
	if err != nil {
		log.Fatalf("resource.Merge failed: %s", err)
	}

	return sdktrace.NewTracerProvider(sdktrace.WithBatcher(exp), sdktrace.WithResource(r))
}

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

func main() {
	// Load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

	// Initializes a new Go Context.
	ctx := context.Background()
	// Create console exporter to print traces to the console.
	// exp, err := newConsoleExporter()
	exp, err := newOTLPExporter(ctx, c.OTLPEndpoint)
	if err != nil {
		log.Fatalf("failed to initialize exporter: %s", err)
	}

	// Create a new tracer provider with a batch span processor and the given exporter.
	tp := newTraceProvider(exp)

	// Handle shutdown properly so nothing leaks.
	defer func() { _ = tp.Shutdown(ctx) }()

	// Registers `tp` as the global trace provider.
	otel.SetTracerProvider(tp)

	// Finally, set the tracer that can be used for this package.
	tracer = tp.Tracer("go-app")

	// Create Prometheus registry
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	// Create Prometheus HTTP server to expose metrics
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	// Start an HTTP server to expose Prometheus metrics in the background.
	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	// Initialize Gin handler.
	h := handler{config: &c, metrics: m}
	h.s3Connect()
	h.dbConnect()

	r := gin.Default()

	// Define handler functions for each endpoint.
	r.GET("/api/devices", h.getDevices)
	r.GET("/api/images", h.getImage)
	r.GET("/health", h.getHealth)

	// Start the main Gin HTTP server.
	log.Printf("Starting App on port %d", c.AppPort)
	r.Run(fmt.Sprintf(":%d", c.AppPort))
}

// getDevices responds with the list of all connected devices as JSON.
func (h *handler) getDevices(c *gin.Context) {
	c.JSON(http.StatusOK, devices())
}

// getImage downloads image from S3
func (h *handler) getImage(c *gin.Context) {
	// Create a new ROOT span to record and trace the request.
	ctx, span := tracer.Start(c, "HTTP GET /api/images")
	defer span.End()

	// Download the image from S3.
	_, ctx, err := download(h.sess, h.config.S3Config.Bucket, "thumbnail.png", h.metrics, ctx)
	if err != nil {
		log.Printf("download failed: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"message": "internal error"})
		return
	}

	// Generate a new image.
	image := NewImage()
	// Save the image ID and the last modified date to the database.
	Save(image, "go_image", h.dbpool, h.metrics, ctx)

	c.JSON(http.StatusOK, gin.H{"message": "saved"})
}

// getHealth responds with a HTTP 200 or 5xx on error.
func (h *handler) getHealth(c *gin.Context) {
	c.JSON(200, gin.H{"status": "up"})
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
	// defer dbpool.Close()

	h.dbpool = dbpool
}
