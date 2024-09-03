package main

import (
	"log"
	"net/http"
	"strconv"
	"strings"
)

func deviceHandler(w http.ResponseWriter, req *http.Request) {
	if req.URL.Path == "/devices/" {
		if req.Method == http.MethodPost {
			createDevice(w, req)
		} else if req.Method == http.MethodGet {
			getAllDevices(w, req)
		} else if req.Method == http.MethodDelete {
			deleteAllDevices(w, req)
		} else {
			http.Error(w, "error...", http.StatusMethodNotAllowed)
			return
		}
	} else {
		path := strings.Trim(req.URL.Path, "/")
		pathParts := strings.Split(path, "/")
		if len(pathParts) < 2 {
			http.Error(w, "error...", http.StatusBadRequest)
			return
		}
		id, err := strconv.Atoi(pathParts[1])
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		if req.Method == http.MethodDelete {
			deleteDevice(w, req, id)
		} else if req.Method == http.MethodGet {
			getDevice(w, req, id)
		} else {
			http.Error(w, "error...", http.StatusMethodNotAllowed)
			return
		}
	}
}

func createDevice(w http.ResponseWriter, req *http.Request) {
	// Placeholder
}

func getAllDevices(w http.ResponseWriter, req *http.Request) {
	// Placeholder
}

func getDevice(w http.ResponseWriter, req *http.Request, id int) {
	// Placeholder
}

func deleteDevice(w http.ResponseWriter, req *http.Request, id int) {
	// Placeholder
}

func deleteAllDevices(w http.ResponseWriter, req *http.Request) {
	// Placeholder
}

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/task/", deviceHandler)

	log.Fatal(http.ListenAndServe(":8080", mux))
}
