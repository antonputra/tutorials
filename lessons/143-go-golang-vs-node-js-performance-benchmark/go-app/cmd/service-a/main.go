package main

import (
	"bytes"
	"encoding/json"
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
	"gopkg.in/yaml.v2"
)

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
	ServiceAPort int `yaml:"serviceAPort"`

	// Base URL for service-b.
	ServiceBBaseUrl string `yaml:"serviceBBaseUrl"`
}

// Message represents the response object
type Message struct {
	// Last modified date of the image.
	LastModified string `json:"lastModified"`
}

func main() {
	// load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

	// initialize handler
	h := handler{config: &c}
	h.connect()

	// setup fiber routes and start http server
	app := fiber.New()
	app.Get("/api/time", h.getTime)
	app.Get("/api/images/:name", h.getImage)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", c.ServiceAPort)))
}

// custom handler to download the image
type handler struct {
	// S3 seesion, should be shared
	sess *session.Session

	// App configuration object
	config *Config
}

// getImage fiber handler to download image
func (h *handler) getImage(c *fiber.Ctx) error {
	name := c.Params("name")

	date, err := download(h.sess, h.config.Bucket, name)
	if err != nil {
		return fmt.Errorf("download failed: %w", err)
	}
	dt := date.Format(time.RFC3339)
	msg := Message{LastModified: dt}

	url := fmt.Sprintf("%s/api/images/%s", h.config.ServiceBBaseUrl, name)

	var buf bytes.Buffer
	err = json.NewEncoder(&buf).Encode(msg)
	if err != nil {
		return fmt.Errorf("json.NewEncoder failed: %w", err)
	}

	r, err := http.Post(url, "application/json", &buf)
	if err != nil {
		return fmt.Errorf("http.Post failed: %w", err)
	}
	defer r.Body.Close()

	if r.StatusCode != 200 {
		bytes, err := io.ReadAll(r.Body)
		if err != nil {
			return fmt.Errorf("io.ReadAll failed: %w", err)
		}
		return fmt.Errorf("service-b: %s", string(bytes))
	}

	err = json.NewDecoder(r.Body).Decode(&msg)
	if err != nil {
		return fmt.Errorf("json.NewDecoder failed: %w", err)
	}

	return c.JSON(msg)
}

// getTime returns current time.
func (h *handler) getTime(c *fiber.Ctx) error {
	url := fmt.Sprintf("%s/api/time", h.config.ServiceBBaseUrl)
	var msg Message

	r, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("http.Get failed: %w", err)
	}
	defer r.Body.Close()

	err = json.NewDecoder(r.Body).Decode(&msg)
	if err != nil {
		return fmt.Errorf("json.NewDecoder failed: %w", err)
	}

	return c.JSON(Message{LastModified: msg.LastModified})
}

// connect initializes the S3 session
func (h *handler) connect() {
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
