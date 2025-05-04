package main

import (
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
)

// Device represents hardware device
type Device struct {
	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

func main() {

	app := fiber.New()
	app.Get("/api/devices", getDevices)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", 8181)))
}

func getDevices(c *fiber.Ctx) error {
	dvs := []Device{
		{"936f1f75-30de-43a8-80b4-d144a8de82ce", "D8-E1-CA-CE-80-21", "1.7.2"},
		{"6fe02683-f79b-4c9f-8409-cf896d9445a0", "14-BA-17-74-24-1D", "2.0.6"},
	}

	return c.JSON(dvs)
}
