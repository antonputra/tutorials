// Package config provides a configuration object for the entire app.
package config

import (
	"app/models"
	"flag"
	"os"

	"github.com/antonputra/go-utils/util"
	"gopkg.in/yaml.v3"
)

// Config is is the top-level configuration object.
type Config struct {
	MetricsPort int               `yaml:"metrics_port"`
	Postgres    PostgresConfig    `yaml:"postgres"`
	Sqlite      SqliteConfig      `yaml:"sqlite"`
	Test        TestConfig        `yaml:"test"`
	Customers   []models.Customer `yaml:"customers"`
	Products    []models.Product  `yaml:"products"`
}

// PostgresConfig is the configuration object for PostgreSQL.
type PostgresConfig struct {
	User           string `yaml:"user"`
	Password       string `yaml:"password"`
	Host           string `yaml:"host"`
	Database       string `yaml:"database"`
	MaxConnections int    `yaml:"max_connections"`
}

// SqliteConfig is the configuration object for SQLite.
type SqliteConfig struct {
	Database    string `yaml:"database"`
	Journal     string `yaml:"journal"`
	Sync        string `yaml:"sync"`
	ForeignKeys int    `yaml:"foreign_keys"`
}

// TestConfig is the configuration object for Test.
type TestConfig struct {
	Interval int `yaml:"interval_s"`
	Delay    int `yaml:"delay_us"`
	Step     int `yaml:"step_us"`
}

// Load parses the YAML configuration and loads it into memory.
func Load() *Config {
	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	data, err := os.ReadFile(*cp)
	util.Fail(err, "failed to read config, path: %s", *cp)

	var cfg Config
	err = yaml.Unmarshal(data, &cfg)
	util.Fail(err, "failed to parse config")

	return &cfg
}
