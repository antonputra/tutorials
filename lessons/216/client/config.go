package main

import (
	"log"
	"os"

	"gopkg.in/yaml.v2"
)

type Config struct {
	Port int      `yaml:"port"`
	Db   DbConfig `yaml:"db"`
	Test Test     `yaml:"test"`
}

type DbConfig struct {
	User           string `yaml:"user"`
	Password       string `yaml:"password"`
	Host           string `yaml:"host"`
	Database       string `yaml:"database"`
	MaxConnections int    `yaml:"maxConnections"`
}

type Test struct {
	Db             string `yaml:"db"`
	Name           string `yaml:"name"`
	MinClients     int    `yaml:"minClients"`
	MaxClients     int    `yaml:"maxClients"`
	StageIntervalS int    `yaml:"stageIntervalS"`
	RequestDelayMs int    `yaml:"requestDelayMs"`
	MaxOrderId     int    `yaml:"maxOrderId"`
}

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
