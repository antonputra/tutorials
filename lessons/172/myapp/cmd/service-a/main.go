package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
)

var target string

// Device represents hardware device
type Device struct {
	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

func init() {
	target = os.Getenv("TARGET")
	if target == "" {
		log.Fatalln("You MUST set TARGET env variable!")
	}
}

func main() {

	app := fiber.New()
	app.Get("/api/devices", getDevices)
	log.Fatalln(app.Listen(fmt.Sprintf(":%d", 8282)))
}

func getDevices(c *fiber.Ctx) error {
	url := fmt.Sprintf("%s/api/devices", target)
	var dvs []Device

	r, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("http.Get failed: %w", err)
	}
	defer r.Body.Close()

	fmt.Println(r.Body)

	err = json.NewDecoder(r.Body).Decode(&dvs)
	if err != nil {
		return fmt.Errorf("json.NewDecoder failed: %w", err)
	}

	return c.JSON(dvs)
}
