package main

import (
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
)

const version string = "v2"

type Response struct {
	Version string `json:"version"`
}

func main() {
	app := fiber.New()
	app.Get("/version", getDevices)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", 8181)))
}

func getDevices(c *fiber.Ctx) error {
	resp := Response{Version: version}

	return c.JSON(resp)
}
