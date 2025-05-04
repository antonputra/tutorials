package rabbitmq

import (
	"client/hardware"
	"client/utils"
	"context"
	"fmt"
	"time"

	"github.com/aristanetworks/goarista/monotime"
	"github.com/google/uuid"
	amqp "github.com/rabbitmq/amqp091-go"
	"google.golang.org/protobuf/proto"
)

func StartProducer(cfg *utils.Config, hostname string) {
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

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	for {
		utils.Sleep(cfg.Test.RequestDelayMs)

		err = ch.PublishWithContext(ctx,
			"",     // exchange
			q.Name, // routing key
			false,  // mandatory
			false,  // immediate
			amqp.Publishing{
				ContentType: "application/octet-stream",
				Body:        device(),
			})
		utils.Warning(err, "ch.PublishWithContext failed")
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
