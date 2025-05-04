package main

import (
	"net/http"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Get("/api/devices", getDevices)
	app.Get("/status", getStatus)

	app.Listen(":8080")
}

// getDevices returns a list of connected devices.
func getDevices(c *fiber.Ctx) error {
	return c.Status(http.StatusOK).JSON(devices())
}

// getStatus returns the status of the application.
func getStatus(c *fiber.Ctx) error {
	return c.Status(http.StatusOK).JSON(&fiber.Map{"status": "ok"})
}
