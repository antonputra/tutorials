package main

import (
	"flag"
	"log"
	"net/http"
	"time"

	pb "github.com/antonputra/tutorials/lessons/152/app/proto"
	"github.com/aristanetworks/goarista/monotime"
	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/protobuf/proto"
)

var (
	brokers = flag.String("kafka-brokers", "localhost", "Apache Kafka brokers.")
	sleep   = flag.String("sleep", "no", "Sleep for a second between retries.")
)

// Prometheus metrics for the application.
type metrics struct {
	// The duration of the producer sending the
	// message and the consumer receiving the message.
	duration *prometheus.SummaryVec
}

// NewMetrics constructs prometheus metrics.
func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		duration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "app",
			Name:       "request_duration_seconds",
			Help:       "Request duration.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"type"}),
	}
	reg.MustRegister(m.duration)
	return m
}

func main() {
	// Get command line arguments.
	flag.Parse()
	// Create a new Prometheus registry.
	reg := prometheus.NewRegistry()
	// Initialize the metrics with the new registry.
	m := NewMetrics(reg)

	// Create a new ServeMux for the Prometheus handler.
	pMux := http.NewServeMux()
	// Create a Prometheus handler with only a defined registry.
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	// Expose Prometheus metrics at /metrics endpoint.
	pMux.Handle("/metrics", promHandler)

	// Run the Prometheus HTTP server in the goroutine.
	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	// Initialize kafka producer.
	p, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": *brokers,
		"acks":              "all",
	})
	if err != nil {
		log.Fatalf("failed to initialize kafka producer: %v", err)
	}
	defer p.Close()

	// Initialize kafka consumer.
	c, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers": *brokers,
		"group.id":          "lesson152",
		"auto.offset.reset": "latest",
	})
	if err != nil {
		log.Fatalf("failed to initialize kafka consumer: %v", err)
	}
	defer c.Close()

	// Define the topic name for the benchmark test.
	topic := "benchmark"
	// Run delivery report.
	go report(p)
	// Start writing messages to kafka.
	go produce(p, topic, 100*time.Millisecond)
	// Start reading messages from kafka.
	go consume(c, m, topic)

	// Prevent exiting from the app.
	select {}
}

// Delivery report handler for produced messages
func report(p *kafka.Producer) {
	// Run for each new event from the producer.
	for e := range p.Events() {
		switch ev := e.(type) {
		case *kafka.Message:
			// If the producer fails to deliver, print the error.
			if ev.TopicPartition.Error != nil {
				log.Printf("Delivery failed: %v\n", ev.TopicPartition)
			}
		}
	}
}

// produce creates and sends a message to the kafka.
func produce(p *kafka.Producer, topic string, interval time.Duration) {
	for {
		// Create new UUID for each new message.
		id := uuid.New().String()
		// Create a imestamp for each new message.
		t := monotime.Now()
		// Create protobuf message to send to the kafka.
		msg := pb.Message{Uuid: id, Created: t}

		// Serialize go struct to proto message.
		b, err := proto.Marshal(&msg)
		if err != nil {
			log.Printf("proto.Marshal failed %v", err)
			return
		}

		// Send protobuf message to the kafka.
		p.Produce(&kafka.Message{
			TopicPartition: kafka.TopicPartition{
				Topic:     &topic,
				Partition: kafka.PartitionAny,
			},
			Value: b,
		}, nil)
		// Sleep for the given interval before repeating.
		if *sleep == "yes" {
			time.Sleep(interval)
		}
	}
}

// consume reads messages from the kafka.
func consume(c *kafka.Consumer, m *metrics, topic string) {
	// Subscribe to the given kafka topic.
	c.SubscribeTopics([]string{topic}, nil)

	for {
		// Fetch the message from kafka.
		msg, err := c.ReadMessage(time.Second)
		if err == nil {
			// Deserialize the kafka message into go struct.
			var message pb.Message
			err := proto.Unmarshal(msg.Value, &message)
			if err != nil {
				log.Printf("proto.Unmarshal failed %v", err)
				return
			}
			// Record the time it took to send and receive the message.
			m.duration.With(prometheus.Labels{"type": "kafka"}).Observe(float64(monotime.Since(message.Created).Seconds()))

		} else if !err.(kafka.Error).IsTimeout() {
			// If the consumer times out, print the error.
			log.Printf("Consumer error: %v (%v)\n", err, msg)
		}
	}
}
