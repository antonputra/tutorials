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

	// DB config to connect to a database.
	DbConfig DbConfig `yaml:"db"`
}

// DbConfig represents configuration for the Postgres
type DbConfig struct {

	// Host to connect database.
	Host string `yaml:"host"`

	// Database to store images.
	Database string `yaml:"database"`

	// Max connections to the database.
	MaxConnections uint64 `yaml:"maxConnections"`
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
