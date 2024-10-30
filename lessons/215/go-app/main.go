package main

import (
	"fmt"
	"log"
	"net/http"

	jsoniter "github.com/json-iterator/go"
)

const port = 8080

// json - jsoniter object
var json = jsoniter.ConfigFastest

// MyServer placeholder.
type MyServer struct{}

func renderJSON(w http.ResponseWriter, value any, status int) {
	w.Header().Set("Content-Type", "application/json")
	content, err := json.Marshal(value)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(status)
	w.Write(content)
}

func main() {
	ms := MyServer{}

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/devices", ms.getDevices)
	mux.HandleFunc("GET /healthz", ms.getHealth)

	appPort := fmt.Sprintf(":%d", port)
	log.Printf("Starting the web server on port %d", port)
	log.Fatal(http.ListenAndServe(appPort, mux))
}

// getHealth returns the status of the application.
func (ms *MyServer) getHealth(w http.ResponseWriter, req *http.Request) {
	// Placeholder for the health check
	w.Write([]byte("OK"))
}

// getDevices returns a list of connected devices.
func (ms *MyServer) getDevices(w http.ResponseWriter, req *http.Request) {
	device := Device{Id: 1, Mac: "EF-2B-C4-F5-D6-34", Firmware: "2.1.5"}

	renderJSON(w, &device, 200)
}
