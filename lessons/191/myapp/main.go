package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

var name string

func init() {
	name = os.Getenv("SERVICE_NAME")
	if name == "" {
		log.Fatalln("You MUST set SERVICE_NAME env variable!")
	}
}

func main() {
	// Echo instance
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())

	// Routes
	e.GET("/about", about)
	e.GET("/poll", poll)

	// Start server
	e.Logger.Fatal(e.Start(":8080"))
}

func about(c echo.Context) error {
	return c.String(http.StatusOK, fmt.Sprintf("%s\n", name))
}

func poll(c echo.Context) error {
	fmt.Printf("Request received by %s\n", name)

	// Sleep for 10 seconds
	time.Sleep(120 * time.Second)

	return c.String(http.StatusOK, fmt.Sprintf("%s\n", name))
}
