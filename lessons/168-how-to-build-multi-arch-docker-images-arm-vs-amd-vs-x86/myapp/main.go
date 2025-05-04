package main

import (
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
)

var (
	version string
)

type Response struct {
	Version string `json:"version"`
}

func init() {
	version = os.Getenv("VERSION")
	if version == "" {
		log.Fatalln("You MUST set VERSION env variable!")
	}
}

func main() {
	app := fiber.New()
	app.Get("/api/version", getVersion)
	app.Get("/health", getHealth)
	app.Listen(":8080")
}

func getVersion(c *fiber.Ctx) error {
	resp := Response{
		Version: version,
	}
	return c.JSON(resp)
}

func getHealth(c *fiber.Ctx) error {
	time.Sleep(3 * time.Second)
	return c.SendStatus(fiber.StatusOK)
}
