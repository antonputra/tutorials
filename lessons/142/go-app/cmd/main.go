package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
)

var (
	service string
	version string
)

type Device struct {
	ID       int    `json:"id"`
	Mac      string `json:"mac"`
	Firmware string `json:"firmware"`
}

type Response struct {
	Version string   `json:"version"`
	Devices []Device `json:"devices"`
}

func init() {
	version = os.Getenv("VERSION")
	service = os.Getenv("SERVICE")
	if service == "" {
		log.Fatalln("You MUST set SERVICE env variable!")
	}
}

func main() {
	app := fiber.New()
	app.Get("/api/devices", getDevices)
	app.Listen(":8080")
}

func getDevices(c *fiber.Ctx) error {
	if service == "service-a" {
		url := "http://service-b.staging:8080/api/devices"
		var resp Response

		r, err := http.Get(url)
		if err != nil {
			log.Fatalln(err)
		}
		defer r.Body.Close()

		err = json.NewDecoder(r.Body).Decode(&resp)
		if err != nil {
			log.Fatalln(err)
		}

		return c.JSON(resp)
	} else {
		dvs := []Device{
			{1, "5F-33-CC-1F-43-82", "2.1.6"},
		}
		resp := Response{
			Devices: dvs,
			Version: version,
		}

		return c.JSON(resp)
	}
}
