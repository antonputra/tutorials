package main

import (
	"os"

	"gopkg.in/yaml.v2"
)

// Config represents a configuration file for the program.
type Config struct {
	// Enable debug mode.
	Debug bool `yaml:"debug"`

	// MetricsPort is the port on which to expose Prometheus metrics.
	MetricsPort int `yaml:"metricsPort"`

	// Postgres is the configuration for PostgreSQL.
	Postgres PostgresConfig `yaml:"pgx"`

	// Mongo is the configuration for MongoDB.
	Mongo MongoConfig `yaml:"mongo"`

	// Test is the configuration for MongoDB.
	Test TestConfig `yaml:"test"`
}

// PostgresConfig represents a configuration file for the PostgreSQL.
type PostgresConfig struct {
	User           string `yaml:"user"`
	Password       string `yaml:"password"`
	Host           string `yaml:"host"`
	Database       string `yaml:"database"`
	MaxConnections int    `yaml:"maxConnections"`
}

type MongoConfig struct {
	// Host to connect database.
	Host string `yaml:"host"`

	// Database to store images.
	Database string `yaml:"database"`

	// Max connections to the database.
	MaxConnections uint64 `yaml:"maxConnections"`
}

type TestConfig struct {
	MinClients     int `yaml:"minClients"`
	MaxClients     int `yaml:"maxClients"`
	StageIntervalS int `yaml:"stageIntervalS"`
	RequestDelayMs int `yaml:"requestDelayMs"`
}

// loadConfig reads the configuration file from the disk into a Go struct.
func (c *Config) loadConfig(path string) {
	// Read the file from the disk.
	f, err := os.ReadFile(path)
	fail(err, "os.ReadFile failed")

	// Convert YAML content to a Go struct.
	err = yaml.Unmarshal(f, c)
	fail(err, "yaml.Unmarshal failed")
}
