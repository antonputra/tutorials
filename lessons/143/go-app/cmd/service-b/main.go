package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"gopkg.in/yaml.v2"
)

// Message represents the response object
type Message struct {
	// Last modified date of the image.
	LastModified string `json:"lastModified"`
}

// Config represents configuration for the app.
type Config struct {
	// Port to run the http server.
	ServiceBPort int `yaml:"serviceBPort"`

	// Mongodb url string
	MongodbURI string `yaml:"mongodbUri"`

	// Base URL for service-a.
	ServiceABaseUrl string `yaml:"serviceABaseUrl"`
}

func main() {
	// load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

	// initialize handler
	h := handler{config: &c}
	h.connect()

	app := fiber.New()
	app.Get("/api/time", h.getTime)
	app.Post("/api/images/:name", h.saveModifiedDate)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", c.ServiceBPort)))
}

// custom handler to save the last modified date
type handler struct {
	// Mongodb client that we can share
	client *mongo.Client

	// App configuration object
	config *Config
}

func (h *handler) saveModifiedDate(c *fiber.Ctx) error {
	var msg Message

	err := c.BodyParser(&msg)
	if err != nil {
		return fmt.Errorf("c.BodyParser failed %w", err)
	}

	err = save(h.client, "lesson143", "images", msg.LastModified)
	if err != nil {
		return fmt.Errorf("save failed: %w", err)
	}

	return c.JSON(msg)
}

// getTime returns current time.
func (h *handler) getTime(c *fiber.Ctx) error {
	now := time.Now()
	dt := now.Format(time.RFC3339)

	return c.JSON(Message{LastModified: dt})
}

// Connect to the mongodb.
func (h *handler) connect() {
	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(h.config.MongodbURI))
	if err != nil {
		log.Fatalf("mongo.Connect failed %v", err)
	}
	h.client = client
}

// save saves the last modified date of the image to the mongodb.
func save(client *mongo.Client, db string, collection string, date string) error {
	coll := client.Database(db).Collection(collection)
	doc := bson.D{{Key: "lastModified", Value: date}}

	_, err := coll.InsertOne(context.TODO(), doc)
	if err != nil {
		return fmt.Errorf("coll.InsertOne failed %w", err)
	}
	return nil
}

// loadConfig loads app config from yaml file.
func (c *Config) loadConfig(path string) {
	f, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("os.ReadFile failed: %v", err)
	}
	err = yaml.Unmarshal(f, c)
	if err != nil {
		log.Fatalf("yaml.Unmarshal failed: %v", err)
	}
}
