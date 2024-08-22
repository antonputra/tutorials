package main

import (
	"log"
	"os"

	"gopkg.in/yaml.v2"
)

type Config struct {
	Url             string  `yaml:"url"`
	RequestInterval int     `yaml:"requestIntervalMs"`
	Stages          []Stage `yaml:"stages"`
}

type Stage struct {
	Clients  int `yaml:"clients"`
	Interval int `yaml:"intervalMin"`
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
