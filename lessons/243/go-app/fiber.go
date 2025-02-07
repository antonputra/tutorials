package main

import (
	"log"

	"github.com/gofiber/fiber/v2"
)

type fiberServer struct {
	*fiber.App
}

func newFiberServer() server {
	f := fiber.New(fiber.Config{
		DisableStartupMessage: true,
		Prefork:               true,
		JSONEncoder:           serializer.Marshal,
		CaseSensitive:         true,
	})

	f.Get("/api/devices", func(c *fiber.Ctx) error {
		return c.JSON(getDevices())
	})

	return &fiberServer{f}
}

func (s *fiberServer) serve(address string) error {
	log.Printf("Starting fiber server on port %s", address)
	return s.Listen(address)
}
