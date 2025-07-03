package main

import (
	"os"

	"github.com/antonputra/go-utils/util"
	"gopkg.in/yaml.v2"
)

type Config struct {
	MetricsPort int             `yaml:"metricsPort"`
	Debug       bool            `yaml:"debug"`
	Redis       RedisConfig     `yaml:"redis"`
	Dragonfly   DragonflyConfig `yaml:"dragonfly"`
	Test        Test            `yaml:"test"`
}

type RedisConfig struct {
	Addr       string   `yaml:"addr"`
	Addrs      []string `yaml:"addrs"`
	Expiration int32    `yaml:"expirationS"`
}

type DragonflyConfig struct {
	Addr       string `yaml:"addr"`
	Expiration int32  `yaml:"expirationS"`
}

type Test struct {
	Name           string `yaml:"name"`
	MinClients     int    `yaml:"minClients"`
	MaxClients     int    `yaml:"maxClients"`
	StageIntervalS int    `yaml:"stageIntervalS"`
	RequestDelayMs int    `yaml:"requestDelayMs"`
}

func (c *Config) loadConfig(path string) {
	f, err := os.ReadFile(path)
	util.Fail(err, "os.ReadFile failed")

	err = yaml.Unmarshal(f, c)
	util.Fail(err, "yaml.Unmarshal failed")
}
