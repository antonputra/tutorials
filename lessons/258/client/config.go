package main

import (
	"os"

	"github.com/antonputra/go-utils/util"
	"gopkg.in/yaml.v2"
)

type Config struct {
	MetricsPort int         `yaml:"metricsPort"`
	Debug       bool        `yaml:"debug"`
	Redis       RedisConfig `yaml:"redis"`
	Test        Test        `yaml:"test"`
}

type RedisConfig struct {
	Expiration int32 `yaml:"expirationS"`
}

type Test struct {
	MinClients     int `yaml:"minClients"`
	MaxClients     int `yaml:"maxClients"`
	StageIntervalS int `yaml:"stageIntervalS"`
	RequestDelayMs int `yaml:"requestDelayMs"`
}

func (c *Config) loadConfig(path string) {
	f, err := os.ReadFile(path)
	util.Fail(err, "os.ReadFile failed")

	err = yaml.Unmarshal(f, c)
	util.Fail(err, "yaml.Unmarshal failed")
}
