package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Device struct {
	ID       int    `json:"id"`
	Mac      string `json:"mac"`
	Firmware string `json:"firmware"`
}

func main() {
	r := gin.Default()
	r.GET("/api/devices", getDevices)
	r.POST("/api/devices", createDevice)
	r.Run(":8001")
}

func getDevices(c *gin.Context) {
	dvs := []Device{
		{1, "5F-33-CC-1F-43-82", "2.1.6"},
		{2, "EF-2B-C4-F5-D6-34", "2.1.6"},
	}

	c.JSON(http.StatusOK, dvs)
}

func createDevice(c *gin.Context) {
	number := 40

	fib := fibonacci(number)

	c.JSON(http.StatusCreated, gin.H{"fib": fib})
}

func fibonacci(n int) int {
	if n <= 1 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}
