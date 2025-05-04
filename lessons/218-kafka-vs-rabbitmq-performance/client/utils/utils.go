package utils

import (
	"fmt"
	"log"
	"math/rand"
	"os"
	"time"

	"gopkg.in/yaml.v2"
)

type Config struct {
	Port     int      `yaml:"port"`
	Test     Test     `yaml:"test"`
	Rabbitmq Rabbitmq `yaml:"rabbitmq"`
	Kafka    Kafka    `yaml:"kafka"`
}

type Kafka struct {
	Version string `yaml:"version"`
	Topic   string `yaml:"topic"`
	Group   string `yaml:"group"`
	Host    string `yaml:"host"`
}

type Rabbitmq struct {
	User        string `yaml:"user"`
	Password    string `yaml:"password"`
	Queue       string `yaml:"queue"`
	Port        int    `yaml:"port"`
	StreamsPort int    `yaml:"streamsPort"`
	Host        string `yaml:"host"`
}

type Test struct {
	Type           string `yaml:"type"`
	RequestDelayMs int    `yaml:"requestDelayMs"`
}

func (c *Config) LoadConfig(path string) {
	f, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("os.ReadFile failed: %v", err)
	}

	err = yaml.Unmarshal(f, c)
	if err != nil {
		log.Fatalf("yaml.Unmarshal failed: %v", err)
	}
}

func Sleep(us int) {
	r := rand.Intn(us)
	time.Sleep(time.Duration(r) * time.Millisecond)
}

func Warning(err error, format string, args ...any) {
	if err != nil {
		log.Printf("%s: %s", fmt.Sprintf(format, args...), err)
	}
}

func Fail(err error, format string, args ...any) {
	if err != nil {
		log.Fatalf("%s: %s", fmt.Sprintf(format, args...), err)
	}
}
