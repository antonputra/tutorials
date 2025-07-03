package kafka

import (
	"client/hardware"
	"client/utils"
	"fmt"

	"github.com/IBM/sarama"
	"github.com/aristanetworks/goarista/monotime"
	"github.com/google/uuid"
	"google.golang.org/protobuf/proto"
)

func StartProducer(cfg *utils.Config, hostname string) {
	version, err := sarama.ParseKafkaVersion(cfg.Kafka.Version)
	utils.Fail(err, "sarama.ParseKafkaVersion failed")

	config := sarama.NewConfig()
	config.Version = version
	config.Producer.Return.Successes = false

	producer, err := sarama.NewAsyncProducer([]string{cfg.Kafka.Host}, config)
	utils.Fail(err, "sarama.NewAsyncProducer failed")

	for {
		utils.Sleep(cfg.Test.RequestDelayMs)
		producer.Input() <- device(fmt.Sprintf("%s-%s", cfg.Kafka.Topic, hostname))
	}
}

func device(topic string) *sarama.ProducerMessage {
	// Create new UUID for each new message.
	id := uuid.New().String()

	// Create a imestamp for each new message.
	t := monotime.Now()

	// Create protobuf message to send to the kafka.
	msg := hardware.Device{Uuid: id, Mac: "85-15-F2-09-AB-E5", Firmware: "2.1.6", CreatedAt: t}

	// Serialize go struct to proto message.
	b, err := proto.Marshal(&msg)
	utils.Warning(err, "proto.Marshal failed")

	return &sarama.ProducerMessage{Topic: topic, Value: sarama.ByteEncoder(b)}
}
