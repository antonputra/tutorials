package main

import (
	"log"
	"net/http"
)

func main() {
	general()
	// generateErrors()
}

func general() {
	for {
		req("GET", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("PUT", "http://api.devopsbyexample.com/devices/123")

		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("GET", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("POST", "http://api.devopsbyexample.com/devices")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")

		req("POST", "http://api.devopsbyexample.com/login")
		req("DELETE", "http://api.devopsbyexample.com/devices/123")
	}
}

func generateErrors() {
	for {
		req("POST", "http://api.devopsbyexample.com/login")
		req("DELETE", "http://api.devopsbyexample.com/devices/123")
		req("PUT", "http://api.devopsbyexample.com/devices/123")
		req("POST", "http://api.devopsbyexample.com/login")
		req("DELETE", "http://api.devopsbyexample.com/devices/123")
		req("POST", "http://api.devopsbyexample.com/login")
		req("DELETE", "http://api.devopsbyexample.com/devices/123")
	}
}

func req(method string, url string) {
	client := &http.Client{}

	req, err := http.NewRequest(method, url, nil)
	if err != nil {
		log.Println(err)
	}
	resp, err := client.Do(req)
	if err != nil {
		log.Println(err)
	}
	defer resp.Body.Close()
}
