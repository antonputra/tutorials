package main

import (
	"fmt"
	"log"

	"github.com/goccy/go-json"
	"github.com/valyala/fasthttp"
)

const port = 8080

// MyServer placeholder
type MyServer struct{}

// renderJSON efficiently serializes the response into JSON and sets the correct headers
func renderJSON(ctx *fasthttp.RequestCtx, value any, status int) {
	// Set the Content-Type header
	ctx.Response.Header.Set("Content-Type", "application/json")
	ctx.SetStatusCode(status)

	// Serialize the value to JSON
	jsonData, err := json.Marshal(value)
	if err != nil {
		ctx.Error(err.Error(), fasthttp.StatusInternalServerError)
		return
	}

	// Write the response
	ctx.Write(jsonData)
}

func main() {
	ms := MyServer{}

	// Start the fasthttp server
	appPort := fmt.Sprintf(":%d", port)
	log.Printf("Starting the web server on port %d", port)

	if err := fasthttp.ListenAndServe(appPort, ms.router); err != nil {
		log.Fatalf("Error in ListenAndServe: %s", err)
	}
}

// router routes the requests based on the URL path
func (ms *MyServer) router(ctx *fasthttp.RequestCtx) {
	switch string(ctx.Path()) {
	case "/api/devices":
		if string(ctx.Method()) == "GET" {
			ms.getDevices(ctx)
		} else {
			ctx.Error("Method not allowed", fasthttp.StatusMethodNotAllowed)
		}
	case "/healthz":
		if string(ctx.Method()) == "GET" {
			ms.getHealth(ctx)
		} else {
			ctx.Error("Method not allowed", fasthttp.StatusMethodNotAllowed)
		}
	default:
		ctx.Error("Not Found", fasthttp.StatusNotFound)
	}
}

// getHealth returns the status of the application.
func (ms *MyServer) getHealth(ctx *fasthttp.RequestCtx) {
	// Placeholder for the health check
	ctx.WriteString("OK")
}

// getDevices returns a list of connected devices.
func (ms *MyServer) getDevices(ctx *fasthttp.RequestCtx) {
	device := Device{Id: 1, Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"}
	renderJSON(ctx, &device, fasthttp.StatusOK)
}
