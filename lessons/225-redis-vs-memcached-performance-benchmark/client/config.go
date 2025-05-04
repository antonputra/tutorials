package main

import (
	"os"

	"gopkg.in/yaml.v2"
)

type Config struct {
	MetricsPort int            `yaml:"metricsPort"`
	Debug       bool           `yaml:"debug"`
	Memcache    MemcacheConfig `yaml:"memcache"`
	Redis       RedisConfig    `yaml:"redis"`
	Test        Test           `yaml:"test"`
}

type MemcacheConfig struct {
	Host       string `yaml:"host"`
	Expiration int32  `yaml:"expirationS"`
}

type RedisConfig struct {
	Host       string `yaml:"host"`
	Expiration int32  `yaml:"expirationS"`
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
	fail(err, "os.ReadFile failed")

	err = yaml.Unmarshal(f, c)
	fail(err, "yaml.Unmarshal failed")
}
