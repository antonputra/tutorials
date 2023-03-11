package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/gofiber/fiber/v2"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"gopkg.in/yaml.v2"
)

type metrics struct {
	devices       prometheus.Counter
	s3Duration    prometheus.Summary
	mongoDuration prometheus.Summary
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		devices: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "goapp",
			Name:      "devices_total",
			Help:      "Number of devices calls.",
		}),
		s3Duration: prometheus.NewSummary(prometheus.SummaryOpts{
			Namespace:  "goapp",
			Name:       "s3_request_duration_seconds",
			Help:       "S3 request duration.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}),
		mongoDuration: prometheus.NewSummary(prometheus.SummaryOpts{
			Namespace:  "goapp",
			Name:       "mongo_request_duration_seconds",
			Help:       "MongoDB request duration.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}),
	}
	reg.MustRegister(m.devices, m.s3Duration, m.mongoDuration)
	return m
}

// Device represents hardware device
type Device struct {
	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

// Config represents configuration for the app.
type Config struct {
	// S3 bucket name to store images.
	Bucket string `yaml:"bucket"`

	// S3 endpoint, since we use Minio we must provide
	// a custom endpoint. It should be a DNS of Minio instance.
	Endpoint string `yaml:"endpoint"`

	// User to access S3 bucket.
	User string `yaml:"user"`

	// Secret to access S3 bucket.
	Secret string `yaml:"secret"`

	// Enable path S3 style; we must enable it to use Minio.
	PathStyle bool `yaml:"pathStyle"`

	// Port to run the http server.
	Port int `yaml:"port"`

	// Mongodb url string
	MongodbURI string `yaml:"mongodbUri"`
}

func main() {
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	// load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

	// initialize handler
	h := handler{config: &c, metrics: m}
	h.s3Connect()
	h.dbConnect()

	app := fiber.New()
	app.Get("/api/devices", getDevices)
	app.Get("/api/images", h.getImage)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", 8080)))
}

func getDevices(c *fiber.Ctx) error {
	dvs := []Device{
		{"b0e42fe7-31a5-4894-a441-007e5256afea", "5F-33-CC-1F-43-82", "2.1.6"},
		{"0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", "EF-2B-C4-F5-D6-34", "2.1.5"},
		{"8c7d519a-38fe-4b7c-946a-a3a88e8fda0e", "FB-0F-1A-F9-8D-04", "2.1.5"},
		{"e64cf5c4-2a54-4267-84ab-5eafb0708e89", "4D-B3-E9-15-34-1F", "2.1.5"},
		{"bd1a945a-e519-442c-a305-63337519deba", "10-03-06-13-10-59", "2.1.2"},
		{"caa0b9c7-33bb-472d-8528-b8dbc569019c", "2B-10-1C-5E-57-54", "2.1.1"},
		{"f0771aa5-9ce2-4d92-a8fa-dd9ea00fe6ab", "4C-60-54-D5-A4-7F", "2.1.6"},
		{"4d3e4528-5c38-4723-baa9-68b8a27ad214", "9B-15-0F-F7-60-CC", "2.1.4"},
		{"67abf1f9-983c-4559-801f-cee90c03b768", "48-1D-BC-54-69-64", "2.2.0"},
		{"21ff6a61-118c-4cf1-86ce-cd6659be81a5", "8C-53-F2-A1-69-93", "2.2.0"},
	}

	return c.JSON(dvs)
}

// custom handler to download the image
type handler struct {
	// Prometheus metrics
	metrics *metrics

	// S3 seesion, should be shared
	sess *session.Session

	// Mongodb client that we can share
	client *mongo.Client

	// App configuration object
	config *Config
}

// getImage fiber handler to download image
func (h *handler) getImage(c *fiber.Ctx) error {
	now := time.Now()
	date, err := download(h.sess, h.config.Bucket, "thumbnail.png")
	if err != nil {
		return fmt.Errorf("download failed: %w", err)
	}
	h.metrics.s3Duration.Observe(time.Since(now).Seconds())

	dt := date.Format(time.RFC3339)

	now = time.Now()
	err = save(h.client, "lesson145", "images", dt)
	if err != nil {
		return fmt.Errorf("save failed: %w", err)
	}
	h.metrics.mongoDuration.Observe(time.Since(now).Seconds())

	return c.SendString("Saved!")
}

// connect initializes the S3 session
func (h *handler) s3Connect() {
	crds := credentials.NewStaticCredentials(h.config.User, h.config.Secret, "")

	s3c := aws.Config{
		Endpoint:         &h.config.Endpoint,
		S3ForcePathStyle: &h.config.PathStyle,
		Credentials:      crds,
	}

	h.sess = session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
		Config:            s3c,
	}))
}

// download downloads S3 image and returns last modified date.
func download(sess *session.Session, bucket string, key string) (*time.Time, error) {
	svc := s3.New(sess)
	input := &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}
	output, err := svc.GetObject(input)
	if err != nil {
		return nil, fmt.Errorf("svc.GetObject failed: %w", err)
	}
	_, err = io.ReadAll(output.Body)
	if err != nil {
		return nil, fmt.Errorf("io.ReadAll failed: %w", err)
	}
	return output.LastModified, nil
}

// Connect to the mongodb.
func (h *handler) dbConnect() {
	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(h.config.MongodbURI))
	if err != nil {
		log.Fatalf("mongo.Connect failed %v", err)
	}
	h.client = client
}

// save saves the last modified date of the image to the mongodb.
func save(client *mongo.Client, db string, collection string, date string) error {
	coll := client.Database(db).Collection(collection)
	doc := bson.D{{Key: "lastModified", Value: date}}

	_, err := coll.InsertOne(context.TODO(), doc)
	if err != nil {
		return fmt.Errorf("coll.InsertOne failed %w", err)
	}
	return nil
}

// loadConfig loads app config from yaml file.
func (c *Config) loadConfig(path string) {
	f, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("os.ReadFile failed: %v", err)
	}
	err = yaml.Unmarshal(f, c)
	if err != nil {
		log.Fatalf("yaml.Unmarshal failed: %v", err)
	}
}
