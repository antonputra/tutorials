package kafka

import (
	"client/hardware"
	"client/metrics"
	"client/utils"
	"context"
	"fmt"
	"log"

	"github.com/IBM/sarama"
	"github.com/aristanetworks/goarista/monotime"
	"github.com/prometheus/client_golang/prometheus"
	"google.golang.org/protobuf/proto"
)

type Consumer struct {
	m *metrics.Metrics
}

func (Consumer) Setup(_ sarama.ConsumerGroupSession) error { return nil }

func (Consumer) Cleanup(_ sarama.ConsumerGroupSession) error { return nil }

func (c Consumer) ConsumeClaim(sess sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {

	for msg := range claim.Messages() {
		// Deserialize the kafka message into go struct.
		var d hardware.Device
		err := proto.Unmarshal(msg.Value, &d)
		if err != nil {
			log.Printf("proto.Unmarshal failed %v", err)
		}

		// Mark message as consumed
		sess.MarkMessage(msg, "")

		// Record the time it took to send and receive the message.
		c.m.Duration.With(prometheus.Labels{"type": "kafka"}).Observe(float64(monotime.Since(d.CreatedAt).Seconds()))
	}

	return nil
}

func StartConsumer(cfg *utils.Config, m *metrics.Metrics, hostname string) {
	version, err := sarama.ParseKafkaVersion(cfg.Kafka.Version)
	utils.Fail(err, "sarama.ParseKafkaVersion failed")

	config := sarama.NewConfig()
	config.Version = version
	config.Consumer.Return.Errors = true

	ctx := context.Background()
	group, err := sarama.NewConsumerGroup([]string{cfg.Kafka.Host}, fmt.Sprintf("%s-%s", cfg.Kafka.Group, hostname), config)
	utils.Fail(err, "sarama.NewConsumerGroup failed")

	go func() {
		for err := range group.Errors() {
			utils.Warning(err, "mc.group.Errors")
		}
	}()

	go func() {
		for {
			topics := []string{fmt.Sprintf("%s-%s", cfg.Kafka.Topic, hostname)}
			handler := Consumer{m: m}

			err := group.Consume(ctx, topics, handler)
			utils.Fail(err, "mc.group.Consume failed")
		}
	}()
}
