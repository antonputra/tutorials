package main

import (
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type Device struct {
	ID  int    `json:"id"`
	MAC string `json:"mac"`
}

var dvs []Device

func init() {
	dvs = append(dvs, Device{ID: 1, MAC: "E9-CF-45-FD-18-B3"})
	dvs = append(dvs, Device{ID: 2, MAC: "CD-6A-9B-70-BF-EA"})
}

func main() {
	r := gin.Default()

	r.GET("/devices", getDevices)
	r.POST("/devices", createDevices)
	r.DELETE("devices/:id", deleteDevice)
	r.PUT("devices/:id", upgradeDevice)

	r.POST("login", login)

	r.Run(":8080")
}

func getDevices(c *gin.Context) {
	sleep(100)
	c.JSON(http.StatusOK, dvs)
}

func createDevices(c *gin.Context) {
	sleep(100)
	c.JSON(http.StatusCreated, gin.H{"message": "Created!"})
}

func upgradeDevice(c *gin.Context) {
	sleep(100)
	c.JSON(http.StatusAccepted, gin.H{"message": "Upgrade started..."})
}

func deleteDevice(c *gin.Context) {
	sleepError(10)
	c.JSON(http.StatusForbidden, gin.H{"message": "failed to delete."})
}

func login(c *gin.Context) {
	sleepError(10)
	c.JSON(http.StatusInternalServerError, gin.H{"message": "Internal error!"})
}

func sleep(ms int) {
	rand.Seed(time.Now().UnixNano())
	now := time.Now()
	n := rand.Intn(ms + now.Second()*2)
	time.Sleep(time.Duration(n) * time.Millisecond)
}

func sleepError(ms int) {
	rand.Seed(time.Now().UnixNano())
	now := time.Now()
	n := rand.Intn(ms + now.Second())
	time.Sleep(time.Duration(n) * time.Millisecond)
}
