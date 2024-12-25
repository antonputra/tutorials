package main

import (
	"os"

	"github.com/antonputra/go-utils/util"
	"gopkg.in/yaml.v2"
)

type Config struct {
	Debug       bool     `yaml:"debug"`
	AppPort     int      `yaml:"appPort"`
	MetricsPort int      `yaml:"metricsPort"`
	Db          DbConfig `yaml:"db"`
	Test        Test     `yaml:"test"`
}

type DbConfig struct {
	User           string `yaml:"user"`
	Password       string `yaml:"password"`
	Host           string `yaml:"host"`
	Database       string `yaml:"database"`
	MaxConnections int    `yaml:"maxConnections"`
}

type Test struct {
	MinClients     int `yaml:"minClients"`
	MaxClients     int `yaml:"maxClients"`
	StageIntervalS int `yaml:"stageIntervalS"`
	RequestDelayMs int `yaml:"requestDelayMs"`
}

func (c *Config) LoadConfig(path string) {
	f, err := os.ReadFile(path)
	util.Fail(err, "failed to read config")

	err = yaml.Unmarshal(f, c)
	util.Fail(err, "failed to parse config")
}
