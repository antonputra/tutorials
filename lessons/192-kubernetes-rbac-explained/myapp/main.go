package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// Device represents hardware device
type Device struct {
	// Universally unique identifier
	UUID string `json:"UUID"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

func main() {
	// Echo instance
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())

	// Routes
	e.GET("/about", about)

	// Start server
	e.Logger.Fatal(e.Start(":8080"))
}

func about(c echo.Context) error {
	d := Device{UUID: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}

	return c.JSON(http.StatusOK, d)
}
