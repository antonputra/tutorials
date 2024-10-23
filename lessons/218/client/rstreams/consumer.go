package rstreams

import (
	"client/hardware"
	"client/metrics"
	"client/utils"
	"fmt"
	"log"

	"github.com/aristanetworks/goarista/monotime"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/rabbitmq/rabbitmq-stream-go-client/pkg/amqp"
	"github.com/rabbitmq/rabbitmq-stream-go-client/pkg/stream"
	"google.golang.org/protobuf/proto"
)

func StartConsumer(cfg *utils.Config, m *metrics.Metrics, hostname string) {
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

	messagesHandler := func(consumerContext stream.ConsumerContext, msg *amqp.Message) {
		// Deserialize the kafka message into go struct.
		var d hardware.Device
		err := proto.Unmarshal(msg.GetData(), &d)
		if err != nil {
			log.Printf("proto.Unmarshal failed %v", err)
		}

		// Record the time it took to send and receive the message.
		m.Duration.With(prometheus.Labels{"type": "rabbitmq"}).Observe(float64(monotime.Since(d.CreatedAt).Seconds()))
	}

	_, err = env.NewConsumer(streamName, messagesHandler, stream.NewConsumerOptions().SetOffset(stream.OffsetSpecification{}.Last()))
	utils.Fail(err, "env.NewConsumer failed")

	select {}
}
