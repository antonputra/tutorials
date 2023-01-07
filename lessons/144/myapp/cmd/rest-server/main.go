package main

import (
	"log"

	pb "github.com/antonputra/tutorials/lessons/143/myapp/device"
	"github.com/gofiber/fiber/v2"
)

func main() {
	h := handler{}
	h.load()

	app := fiber.New()
	app.Get("/api/devices", h.getArticles)
	log.Fatalln(app.Listen(":8080"))
}

type handler struct {
	dvs []pb.Device
}

func (h *handler) getArticles(c *fiber.Ctx) error {
	return c.JSON(h.dvs)
}

func (h *handler) load() {
	h.dvs = []pb.Device{
		{Uuid: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Uuid: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"},
		{Uuid: "8c7d519a-38fe-4b7c-946a-a3a88e8fda0e", Mac: "FB-0F-1A-F9-8D-04", Firmware: "2.1.5"},
		{Uuid: "e64cf5c4-2a54-4267-84ab-5eafb0708e89", Mac: "4D-B3-E9-15-34-1F", Firmware: "2.1.5"},
		{Uuid: "bd1a945a-e519-442c-a305-63337519deba", Mac: "10-03-06-13-10-59", Firmware: "2.1.2"},
		{Uuid: "caa0b9c7-33bb-472d-8528-b8dbc569019c", Mac: "2B-10-1C-5E-57-54", Firmware: "2.1.1"},
		{Uuid: "f0771aa5-9ce2-4d92-a8fa-dd9ea00fe6ab", Mac: "4C-60-54-D5-A4-7F", Firmware: "2.1.6"},
		{Uuid: "4d3e4528-5c38-4723-baa9-68b8a27ad214", Mac: "9B-15-0F-F7-60-CC", Firmware: "2.1.4"},
		{Uuid: "67abf1f9-983c-4559-801f-cee90c03b768", Mac: "48-1D-BC-54-69-64", Firmware: "2.2.0"},
		{Uuid: "21ff6a61-118c-4cf1-86ce-cd6659be81a5", Mac: "8C-53-F2-A1-69-93", Firmware: "2.2.0"},
	}
}
