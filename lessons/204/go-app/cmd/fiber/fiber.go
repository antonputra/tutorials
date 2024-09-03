package main

import (
	"go-stdlib/device"
	"log"

	"github.com/gofiber/fiber/v3"
)

type server struct {
	state int
}

func NewServer() *server {
	state := 0
	return &server{state: state}
}

// getDevices returns a list of connected devices.
func (s *server) getDevices(c fiber.Ctx) error {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
		{Id: 2, Mac: "62-46-13-B7-B3-A1", Firmware: "3.0.0"},
		{Id: 3, Mac: "96-A8-DE-5B-77-14", Firmware: "1.0.1"},
		{Id: 4, Mac: "7E-3B-62-A6-09-12", Firmware: "3.5.6"},
	}

	return c.Status(fiber.StatusOK).JSON(devices)
}

// getHealth returns the status of the application.
func (s *server) getHealth(c fiber.Ctx) error {
	// Placeholder for the health check
	return c.SendStatus(200)
}

func (s *server) getInfo(c fiber.Ctx) error {
	// Placeholder for the health check
	return c.SendString("fiber")
}

func main() {
	app := fiber.New()
	s := NewServer()

	app.Get("/devices", s.getDevices)
	app.Get("/healthz", s.getHealth)
	app.Get("/about", s.getInfo)

	log.Fatal(app.Listen(":8080"))
}
