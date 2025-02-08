package main

import (
	"log"
	"net/http"

	"git.akyoto.dev/go/web"
)

type webServer struct {
	web.Server
}

func newWebServer() server {
	r := web.NewServer()

	r.Get("/api/devices", func(c web.Context) error {
		devices, err := serializer.Marshal(getDevices())
		if err != nil {
			return err
		}

		c.Response().SetHeader("Content-Type", "application/json")
		c.Response().SetStatus(http.StatusOK)
		return c.Bytes(devices)
	})

	return &webServer{r}
}

func (s *webServer) serve(address string) error {
	log.Printf("Starting go/web server on port %s", address)
	return s.Run(address)
}
