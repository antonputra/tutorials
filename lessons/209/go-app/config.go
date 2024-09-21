package main

import (
	"log"
	"os"

	"gopkg.in/yaml.v2"
)

// Config represents configuration for the app.
type Config struct {

	// Port to run the http server.
	AppPort int `yaml:"appPort"`

	// Port to expose Prometheus metrics.
	MetricsPort int `yaml:"metricsPort"`

	// S3 config to connect to a bucket.
	S3Config S3Config `yaml:"s3"`

	// DB config to connect to a database.
	DbConfig DbConfig `yaml:"db"`
}

// S3Config represents configuration for the S3.
type S3Config struct {

	// Region for the S3 bucket.
	Region string `yaml:"region"`

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

	// Path for the image.
	ImagePath string `yaml:"imgPath"`
}

// DbConfig represents configuration for the Postgres
type DbConfig struct {

	// User to connect database.
	User string `yaml:"user"`

	// Password to connect database.
	Password string `yaml:"password"`

	// Host to connect database.
	Host string `yaml:"host"`

	// Database to store images.
	Database string `yaml:"database"`
}

// loadConfig loads app config from YAML file.
func (c *Config) loadConfig(path string) {

	// Read the config file from the disk.
	f, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("os.ReadFile failed: %v", err)
	}

	// Convert the YAML config into a Go struct.
	err = yaml.Unmarshal(f, c)
	if err != nil {
		log.Fatalf("yaml.Unmarshal failed: %v", err)
	}
}
