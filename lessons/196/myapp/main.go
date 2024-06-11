package main

import (
	"fmt"
	"strconv"

	"github.com/gofiber/fiber/v2"
)

var (
	port    = 8080
	name    = "myapp"
	version = "v0.1.4"
)

func init() {}

type handler struct{}

func main() {
	app := fiber.New()

	h := handler{}

	app.Get("/api/cpu", h.cpu)
	app.Get("/about", h.about)
	app.Get("/health", h.health)

	app.Listen(fmt.Sprintf(":%d", port))
}

func (h *handler) cpu(c *fiber.Ctx) error {
	index := c.Query("index")
	i, err := strconv.Atoi(index)
	if err != nil {
		return fmt.Errorf("strconv.Atoi failed: %w", err)
	}

	n := fib(i)
	msg := fmt.Sprintf("Testing CPU load: Fibonacci index is %d, number is %d", i, n)

	return c.JSON(&fiber.Map{"message": msg})
}

func (h *handler) about(c *fiber.Ctx) error {
	return c.JSON(&fiber.Map{"service": name, "version:": version})
}

func (h *handler) health(c *fiber.Ctx) error {
	return c.JSON(&fiber.Map{"status": "ok"})
}

func fib(n int) int {
	if n <= 1 {
		return n
	}
	return fib(n-1) + fib(n-2)
}
