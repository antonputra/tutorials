package main

import (
	"client/kafka"
	"client/metrics"
	"client/rabbitmq"
	"client/rstreams"
	"client/utils"
	"log"
	"os"

	"github.com/prometheus/client_golang/prometheus"
)

var (
	client   string
	hostname string
)

func init() {
	client = os.Getenv("CLIENT")
	if client == "" {
		log.Fatalln("You MUST set CLIENT env variable!")
	}
	hostname = os.Getenv("HOSTNAME")
	if client == "" {
		log.Fatalln("You MUST set HOSTNAME env variable!")
	}
}

func main() {
	cfg := new(utils.Config)
	cfg.LoadConfig("config.yaml")

	reg := prometheus.NewRegistry()
	m := metrics.NewMetrics(reg)
	metrics.StartPrometheusServer(cfg, reg)

	switch client {
	case "kafka":
		kafka.StartConsumer(cfg, m, hostname)
		kafka.StartProducer(cfg, hostname)
		log.Printf("Starting %s producer and consumer", client)

	case "rabbitmq":
		go rabbitmq.StartProducer(cfg, hostname)
		rabbitmq.StartConsumer(cfg, m, hostname)
		log.Printf("Starting %s producer and consumer", client)

	case "rabbitmq-streams":
		go rstreams.StartProducer(cfg, hostname)
		rstreams.StartConsumer(cfg, m, hostname)
		log.Printf("Starting %s producer and consumer", client)

	default:
		log.Fatalf("%s client is NOT supported", client)
	}
}
