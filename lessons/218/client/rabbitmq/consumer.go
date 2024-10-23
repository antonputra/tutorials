package rabbitmq

import (
	"client/hardware"
	"client/metrics"
	"client/utils"
	"fmt"
	"log"

	"github.com/aristanetworks/goarista/monotime"
	"github.com/prometheus/client_golang/prometheus"
	amqp "github.com/rabbitmq/amqp091-go"
	"google.golang.org/protobuf/proto"
)

func StartConsumer(cfg *utils.Config, m *metrics.Metrics, hostname string) {
	uri := fmt.Sprintf("amqp://%s:%s@%s:%d/", cfg.Rabbitmq.User, cfg.Rabbitmq.Password, cfg.Rabbitmq.Host, cfg.Rabbitmq.Port)
	conn, err := amqp.Dial(uri)
	utils.Fail(err, "amqp.Dial failed")
	defer conn.Close()

	ch, err := conn.Channel()
	utils.Fail(err, "conn.Channel failed")
	defer ch.Close()

	q, err := ch.QueueDeclare(
		fmt.Sprintf("%s-%s", cfg.Rabbitmq.Queue, hostname), // name
		false, // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	utils.Fail(err, "ch.QueueDeclare failed")

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	utils.Warning(err, "ch.Consume failed")

	for msg := range msgs {
		// Deserialize the kafka message into go struct.
		var d hardware.Device
		err := proto.Unmarshal(msg.Body, &d)
		if err != nil {
			log.Printf("proto.Unmarshal failed %v", err)
		}

		// Record the time it took to send and receive the message.
		m.Duration.With(prometheus.Labels{"type": "rabbitmq"}).Observe(float64(monotime.Since(d.CreatedAt).Seconds()))
	}
}
