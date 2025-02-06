package main

import (
	"os"

	"github.com/antonputra/go-utils/util"
	"gopkg.in/yaml.v2"
)

type Config struct {
	Debug   bool `yaml:"debug"`
	AppPort int  `yaml:"appPort"`
}

func (c *Config) LoadConfig(path string) {
	f, err := os.ReadFile(path)
	util.Fail(err, "failed to read config")

	err = yaml.Unmarshal(f, c)
	util.Fail(err, "failed to parse config")
}
