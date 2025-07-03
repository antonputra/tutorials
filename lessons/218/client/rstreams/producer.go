package rstreams

import (
	"client/hardware"
	"client/utils"
	"fmt"

	"github.com/aristanetworks/goarista/monotime"
	"github.com/google/uuid"
	"github.com/rabbitmq/rabbitmq-stream-go-client/pkg/amqp"
	"github.com/rabbitmq/rabbitmq-stream-go-client/pkg/stream"
	"google.golang.org/protobuf/proto"
)

func StartProducer(cfg *utils.Config, hostname string) {
	env, err := stream.NewEnvironment(
		stream.NewEnvironmentOptions().
			SetHost(cfg.Rabbitmq.Host).
			SetPort(cfg.Rabbitmq.StreamsPort).
			SetUser(cfg.Rabbitmq.User).
			SetPassword(cfg.Rabbitmq.Password))
	utils.Fail(err, "stream.NewEnvironment failed")

	streamName := fmt.Sprintf("%s-%s", cfg.Rabbitmq.Queue, hostname)
	err = env.DeclareStream(streamName,
		&stream.StreamOptions{
			MaxLengthBytes: stream.ByteCapacity{}.GB(1),
		},
	)
	utils.Fail(err, "env.DeclareStream failed")

	producer, err := env.NewProducer(streamName, stream.NewProducerOptions())
	utils.Fail(err, "env.NewProducer failed")

	for {
		utils.Sleep(cfg.Test.RequestDelayMs)
		err = producer.Send(amqp.NewMessage(device()))
		utils.Warning(err, "producer.Send failed")
	}
}

func device() []byte {
	// Create new UUID for each new message.
	id := uuid.New().String()

	// Create a imestamp for each new message.
	t := monotime.Now()

	// Create protobuf message to send to the kafka.
	msg := hardware.Device{Uuid: id, Mac: "85-15-F2-09-AB-E5", Firmware: "2.1.6", CreatedAt: t}

	// Serialize go struct to proto message.
	b, err := proto.Marshal(&msg)
	utils.Warning(err, "proto.Marshal failed")

	return b
}
