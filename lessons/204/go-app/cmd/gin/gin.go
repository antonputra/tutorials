package main

import (
	"go-stdlib/device"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

type server struct {
	state int
}

func NewServer() *server {
	state := 0
	return &server{state: state}
}

func (s *server) getDevices(c *gin.Context) {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
		{Id: 2, Mac: "62-46-13-B7-B3-A1", Firmware: "3.0.0"},
		{Id: 3, Mac: "96-A8-DE-5B-77-14", Firmware: "1.0.1"},
		{Id: 4, Mac: "7E-3B-62-A6-09-12", Firmware: "3.5.6"},
	}

	c.JSON(http.StatusOK, devices)
}

func (s *server) getHealth(c *gin.Context) {
	c.String(http.StatusOK, "OK")
}

func (s *server) getInfo(c *gin.Context) {
	c.String(http.StatusOK, "gin")
}

func main() {
	app := gin.Default()
	s := NewServer()

	app.GET("/devices", s.getDevices)
	app.GET("/healthz", s.getHealth)
	app.GET("/about", s.getInfo)

	log.Fatal(app.Run(":8080"))
}
